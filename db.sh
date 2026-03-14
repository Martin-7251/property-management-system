#!/bin/bash

# ============================================================================
# Property Management System - Database Helper Scripts
# ============================================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Database connection details
CONTAINER_NAME="property_mgmt_db"
DB_USER="prop_mgmt_user"
DB_NAME="property_management"

# ============================================================================
# FUNCTIONS
# ============================================================================

# Start database
start_db() {
    echo -e "${GREEN}Starting database containers...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Database started${NC}"
    echo -e "PostgreSQL: http://localhost:5432"
    echo -e "pgAdmin: http://localhost:5050"
}

# Stop database
stop_db() {
    echo -e "${YELLOW}Stopping database containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Database stopped${NC}"
}

# Restart database
restart_db() {
    echo -e "${YELLOW}Restarting database...${NC}"
    docker-compose restart postgres
    echo -e "${GREEN}✓ Database restarted${NC}"
}

# View logs
view_logs() {
    echo -e "${GREEN}Viewing PostgreSQL logs (Ctrl+C to exit)...${NC}"
    docker-compose logs -f postgres
}

# Connect to database shell
connect_db() {
    echo -e "${GREEN}Connecting to database...${NC}"
    docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME
}

# Check database status
check_status() {
    echo -e "${GREEN}Database Status:${NC}"
    docker-compose ps
    echo ""
    echo -e "${GREEN}Database Health:${NC}"
    docker exec $CONTAINER_NAME pg_isready -U $DB_USER -d $DB_NAME
}

# List all tables
list_tables() {
    echo -e "${GREEN}Listing all tables...${NC}"
    docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "\dt"
}

# Count records in all tables
count_records() {
    echo -e "${GREEN}Counting records in all tables...${NC}"
    docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME << 'EOF'
SELECT 
    schemaname,
    tablename,
    (xpath('/row/cnt/text()', xml_count))[1]::text::int AS row_count
FROM (
    SELECT 
        table_schema AS schemaname,
        table_name AS tablename,
        query_to_xml(
            format('SELECT COUNT(*) AS cnt FROM %I.%I', table_schema, table_name),
            false,
            true,
            ''
        ) AS xml_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
) t
ORDER BY tablename;
EOF
}

# Backup database
backup_db() {
    BACKUP_DIR="./backups"
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"
    
    echo -e "${GREEN}Creating backup...${NC}"
    docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
        
        # Compress backup
        gzip $BACKUP_FILE
        echo -e "${GREEN}✓ Backup compressed: ${BACKUP_FILE}.gz${NC}"
    else
        echo -e "${RED}✗ Backup failed${NC}"
    fi
}

# Restore database from backup
restore_db() {
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lh ./backups/*.sql.gz 2>/dev/null || ls -lh ./backups/*.sql 2>/dev/null
    
    read -p "Enter backup filename (e.g., backup_20260203_123456.sql.gz): " BACKUP_FILE
    
    if [ ! -f "./backups/$BACKUP_FILE" ]; then
        echo -e "${RED}✗ Backup file not found!${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}⚠ This will REPLACE all current data!${NC}"
    read -p "Are you sure? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}Restore cancelled${NC}"
        return 0
    fi
    
    # Check if file is compressed
    if [[ $BACKUP_FILE == *.gz ]]; then
        echo -e "${GREEN}Decompressing and restoring...${NC}"
        gunzip -c "./backups/$BACKUP_FILE" | docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME
    else
        echo -e "${GREEN}Restoring...${NC}"
        docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME < "./backups/$BACKUP_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database restored successfully${NC}"
    else
        echo -e "${RED}✗ Restore failed${NC}"
    fi
}

# Reset database (WARNING: Deletes all data!)
reset_db() {
    echo -e "${RED}⚠⚠⚠ WARNING ⚠⚠⚠${NC}"
    echo -e "${RED}This will DELETE ALL DATA and recreate the database!${NC}"
    read -p "Type 'DELETE ALL DATA' to confirm: " CONFIRM
    
    if [ "$CONFIRM" != "DELETE ALL DATA" ]; then
        echo -e "${YELLOW}Reset cancelled${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Stopping containers...${NC}"
    docker-compose down -v
    
    echo -e "${GREEN}Restarting with fresh database...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✓ Database reset complete${NC}"
}

# Run custom SQL query
run_query() {
    read -p "Enter SQL query: " QUERY
    docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "$QUERY"
}

# Show help menu
show_help() {
    echo -e "${GREEN}Property Management Database Helper${NC}"
    echo ""
    echo "Usage: ./db.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start          - Start database containers"
    echo "  stop           - Stop database containers"
    echo "  restart        - Restart database"
    echo "  status         - Check database status"
    echo "  logs           - View database logs"
    echo "  connect        - Connect to database shell"
    echo "  tables         - List all tables"
    echo "  count          - Count records in all tables"
    echo "  backup         - Create database backup"
    echo "  restore        - Restore database from backup"
    echo "  reset          - Reset database (DELETE ALL DATA)"
    echo "  query          - Run custom SQL query"
    echo "  help           - Show this help menu"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

case "$1" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    connect)
        connect_db
        ;;
    tables)
        list_tables
        ;;
    count)
        count_records
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db
        ;;
    reset)
        reset_db
        ;;
    query)
        run_query
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac