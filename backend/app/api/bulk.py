"""
Bulk Upload API Routes
Endpoints for importing multiple records via CSV/Excel files
Supports both .csv and .xlsx/.xls files
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime, date

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.api.deps import get_current_user

router = APIRouter()


def read_upload_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Read uploaded file (CSV or Excel) and return pandas DataFrame
    """
    try:
        if filename.endswith('.csv'):
            # Try UTF-8 first, then fall back to other encodings
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8-sig')
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(file_content), encoding='latin-1')
        elif filename.endswith(('.xlsx', '.xls')):
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")
        
        return df
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        )


@router.post("/bulk/properties")
async def bulk_upload_properties(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk upload properties from CSV or Excel file.
    
    Supported formats: .csv, .xlsx, .xls
    
    Required columns:
    - name: Property name
    - address: Property address
    
    Optional columns:
    - type: Property type (will be added to description)
    - total_units: Number of units (will be added to description)
    """
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(400, "Only CSV and Excel files are supported (.csv, .xlsx, .xls)")
    
    # Read file
    content = await file.read()
    df = read_upload_file(content, file.filename)
    
    success_count = 0
    failed_count = 0
    errors = []
    
    # Validate required columns
    required_columns = ['name', 'address']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            400,
            f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    for index, row in df.iterrows():
        try:
            # Skip empty rows
            if pd.isna(row['name']) or pd.isna(row['address']):
                errors.append(f"Row {index + 2}: Missing name or address")
                failed_count += 1
                continue
            
            # Build description from type and units info
            description_parts = []
            if pd.notna(row.get('type')):
                description_parts.append(f"Type: {row['type']}")
            if pd.notna(row.get('total_units')):
                description_parts.append(f"Total Units: {row['total_units']}")
            
            description = "; ".join(description_parts) if description_parts else None
            
            # Create property
            property = Property(
                landlord_id=current_user.id,
                name=str(row['name']).strip(),
                address=str(row['address']).strip(),
                description=description,
            )
            
            db.add(property)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            failed_count += 1
    
    # Commit all successful records
    if success_count > 0:
        db.commit()
    
    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors[:10],  # Return first 10 errors
        "message": f"Imported {success_count} properties successfully"
    }


@router.post("/bulk/units")
async def bulk_upload_units(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk upload units from CSV or Excel file.
    
    Supported formats: .csv, .xlsx, .xls
    
    Required columns:
    - property_name: Name of existing property
    - unit_number: Unit identifier (e.g., A101, B2)
    - bedrooms: Number of bedrooms
    - bathrooms: Number of bathrooms
    - rent_amount: Monthly rent amount (will be saved as base_rent)
    - status: vacant or occupied (will be converted to is_available)
    """
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(400, "Only CSV and Excel files are supported (.csv, .xlsx, .xls)")
    
    # Read file
    content = await file.read()
    df = read_upload_file(content, file.filename)
    
    # Get user's properties for lookup
    properties = db.query(Property).filter(Property.landlord_id == current_user.id).all()
    property_map = {p.name: p.id for p in properties}
    
    success_count = 0
    failed_count = 0
    errors = []
    
    # Validate required columns
    required_columns = ['property_name', 'unit_number', 'bedrooms', 'bathrooms', 'rent_amount', 'status']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            400,
            f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    for index, row in df.iterrows():
        try:
            property_name = str(row.get('property_name', '')).strip()
            
            # Skip empty rows
            if pd.isna(row['property_name']) or pd.isna(row['unit_number']):
                errors.append(f"Row {index + 2}: Missing property name or unit number")
                failed_count += 1
                continue
            
            # Find property
            if property_name not in property_map:
                errors.append(f"Row {index + 2}: Property '{property_name}' not found")
                failed_count += 1
                continue
            
            # Parse status to is_available
            status = str(row.get('status', 'vacant')).strip().lower()
            is_available = status == 'vacant'
            
            # Create unit
            unit = Unit(
                property_id=property_map[property_name],
                unit_number=str(row['unit_number']).strip(),
                bedrooms=int(row.get('bedrooms', 1)),
                bathrooms=int(row.get('bathrooms', 1)),
                base_rent=float(row.get('rent_amount', 0)),
                is_available=is_available
            )
            
            db.add(unit)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            failed_count += 1
    
    if success_count > 0:
        db.commit()
    
    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors[:10],
        "message": f"Imported {success_count} units successfully"
    }


@router.post("/bulk/tenants")
async def bulk_upload_tenants(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk upload tenants from CSV or Excel file.
    
    Supported formats: .csv, .xlsx, .xls
    
    Required columns:
    - property_name
    - unit_number
    - full_name
    - phone
    - email (optional)
    - id_number (optional)
    - base_rent
    - security_deposit_amount
    - move_in_date (optional)
    """
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(400, "Only CSV and Excel files are supported (.csv, .xlsx, .xls)")
    
    # Read file
    content = await file.read()
    df = read_upload_file(content, file.filename)
    
    # Get properties and units for lookup
    properties = db.query(Property).filter(Property.landlord_id == current_user.id).all()
    property_map = {p.name: p for p in properties}
    
    # Build unit lookup: {property_name: {unit_number: unit}}
    unit_map = {}
    for prop in properties:
        units = db.query(Unit).filter(Unit.property_id == prop.id).all()
        unit_map[prop.name] = {u.unit_number: u for u in units}
    
    success_count = 0
    failed_count = 0
    errors = []
    
    # Validate required columns
    required_columns = ['property_name', 'unit_number', 'full_name', 'phone', 'base_rent', 'security_deposit_amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            400,
            f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    for index, row in df.iterrows():
        try:
            property_name = str(row.get('property_name', '')).strip()
            unit_number = str(row.get('unit_number', '')).strip()
            
            # Skip empty rows
            if pd.isna(row['property_name']) or pd.isna(row['unit_number']) or pd.isna(row['full_name']):
                errors.append(f"Row {index + 2}: Missing required fields")
                failed_count += 1
                continue
            
            # Find property and unit
            if property_name not in property_map:
                errors.append(f"Row {index + 2}: Property '{property_name}' not found")
                failed_count += 1
                continue
            
            if property_name not in unit_map or unit_number not in unit_map[property_name]:
                errors.append(f"Row {index + 2}: Unit '{unit_number}' not found in '{property_name}'")
                failed_count += 1
                continue
            
            unit = unit_map[property_name][unit_number]
            
            # Check for duplicate tenant (by unit_id with active status)
            existing_tenant = db.query(Tenant).filter(
                Tenant.unit_id == unit.id,
                Tenant.status.in_(['pending', 'active'])
            ).first()
            
            if existing_tenant:
                errors.append(f"Row {index + 2}: Active tenant already exists in unit '{unit_number}' ({existing_tenant.full_name})")
                failed_count += 1
                continue
            
            # Parse move_in_date properly
            move_in_date = None
            if pd.notna(row.get('move_in_date')):
                try:
                    # Parse date from pandas and convert to date object
                    date_value = pd.to_datetime(row.get('move_in_date'))
                    move_in_date = date_value.date()  # Convert to date object
                except:
                    # If parsing fails, try manual parsing
                    try:
                        date_str = str(row.get('move_in_date'))
                        move_in_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except:
                        pass  # Leave as None if can't parse
            
            # Clean phone number (remove .0 if it's a float)
            phone = str(row['phone']).strip()
            if phone.endswith('.0'):
                phone = phone[:-2]
            
            # Ensure phone starts with +
            if not phone.startswith('+'):
                phone = '+' + phone
            
            # Create tenant
            tenant = Tenant(
                unit_id=unit.id,
                property_id=property_map[property_name].id,
                full_name=str(row['full_name']).strip(),
                phone=phone,
                email=str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,
                id_number=str(row.get('id_number', '')).strip() if pd.notna(row.get('id_number')) else None,
                base_rent=float(row.get('base_rent', 0)),
                security_deposit_amount=float(row.get('security_deposit_amount', 0)),
                security_deposit_paid=False,
                move_in_date=move_in_date,  # Now a date object
                status='active'  # Set as active when importing
            )
            
            db.add(tenant)
            
            # Update unit availability
            unit.is_available = False
            
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {index + 2}: {str(e)}")
            failed_count += 1
    
    if success_count > 0:
        db.commit()
    
    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors[:10],
        "message": f"Imported {success_count} tenants successfully"
    }