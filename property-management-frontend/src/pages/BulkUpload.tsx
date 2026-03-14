import React, { useState, useRef } from 'react';
import { Upload, Download, FileText, Building2, Home, Users, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { bulkUploadService } from '../services/bulkUpload.service';
import toast from 'react-hot-toast';

type UploadType = 'properties' | 'units' | 'tenants';

interface UploadResult {
  success: number;
  failed: number;
  errors: string[];
}

export const BulkUpload: React.FC = () => {
  const [selectedType, setSelectedType] = useState<UploadType>('properties');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadTypes = [
    {
      id: 'properties' as UploadType,
      name: 'Properties',
      icon: Building2,
      description: 'Import properties with name and address',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      id: 'units' as UploadType,
      name: 'Units',
      icon: Home,
      description: 'Import units with property name and rent',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      id: 'tenants' as UploadType,
      name: 'Tenants',
      icon: Users,
      description: 'Import tenants with full details',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  const currentType = uploadTypes.find(t => t.id === selectedType)!;

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    
    if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.csv')) {
      toast.error('Please upload a CSV or Excel file');
      return;
    }

    setFile(selectedFile);
    setResult(null);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setUploading(true);
    setResult(null);

    try {
      let response;
      
      switch (selectedType) {
        case 'properties':
          response = await bulkUploadService.uploadProperties(file);
          break;
        case 'units':
          response = await bulkUploadService.uploadUnits(file);
          break;
        case 'tenants':
          response = await bulkUploadService.uploadTenants(file);
          break;
      }

      setResult({
        success: response.success || 0,
        failed: response.failed || 0,
        errors: response.errors || [],
      });

      if (response.success > 0) {
        toast.success(`Successfully imported ${response.success} ${selectedType}!`);
      }
      
      if (response.failed > 0) {
        toast.error(`Failed to import ${response.failed} ${selectedType}`);
      }

      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = () => {
    bulkUploadService.downloadTemplate(selectedType);
    toast.success(`${currentType.name} template downloaded!`);
  };

  return (
    <div>
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Upload className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Bulk Upload</h1>
              <p className="text-gray-600 mt-1">
                Import multiple records at once using CSV or Excel files
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Select Type</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-2 p-4">
                  {uploadTypes.map((type) => {
                    const Icon = type.icon;
                    return (
                      <button
                        key={type.id}
                        onClick={() => {
                          setSelectedType(type.id);
                          setFile(null);
                          setResult(null);
                        }}
                        className={`w-full flex items-start gap-3 p-4 rounded-lg border-2 transition-all ${
                          selectedType === type.id
                            ? 'border-primary-600 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300 bg-white'
                        }`}
                      >
                        <div className={`w-10 h-10 ${type.bgColor} rounded-lg flex items-center justify-center flex-shrink-0`}>
                          <Icon className={`w-5 h-5 ${type.color}`} />
                        </div>
                        <div className="text-left">
                          <p className="font-medium text-gray-900">{type.name}</p>
                          <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Download Template */}
            <Card className="mt-6">
              <CardContent>
                <div className="text-center">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <h3 className="font-medium text-gray-900 mb-2">Need a Template?</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Download a sample CSV file
                  </p>
                  <Button onClick={handleDownloadTemplate} variant="outline" className="w-full">
                    <Download className="w-4 h-4" />
                    Download Template
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Side */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Area */}
            <Card>
              <CardHeader>
                <CardTitle>Upload {currentType.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg p-8 transition-all ${
                    dragActive
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="text-center">
                    <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    
                    {file ? (
                      <div>
                        <p className="text-lg font-medium text-gray-900 mb-2">
                          {file.name}
                        </p>
                        <p className="text-sm text-gray-500 mb-4">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                        <div className="flex gap-3 justify-center">
                          <Button onClick={handleUpload} variant="primary" loading={uploading}>
                            <Upload className="w-4 h-4" />
                            Upload File
                          </Button>
                          <Button
                            onClick={() => {
                              setFile(null);
                              if (fileInputRef.current) {
                                fileInputRef.current.value = '';
                              }
                            }}
                            variant="outline"
                            disabled={uploading}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <p className="text-lg font-medium text-gray-900 mb-2">
                          Drag and drop your file here
                        </p>
                        <p className="text-sm text-gray-500 mb-4">
                          or click to browse
                        </p>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept=".csv,.xlsx,.xls"
                          onChange={handleFileInputChange}
                          className="hidden"
                          id="file-upload"
                        />
                        <label htmlFor="file-upload">
                          <span className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors cursor-pointer font-medium">
                            <Upload className="w-4 h-4" />
                            Choose File
                          </span>
                        </label>
                        <p className="text-xs text-gray-500 mt-4">
                          Supports CSV and Excel files
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Results */}
            {result && (
              <Card>
                <CardHeader>
                  <CardTitle>Upload Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                        <div>
                          <p className="text-2xl font-bold text-green-900">{result.success}</p>
                          <p className="text-sm text-green-700">Successful</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 bg-red-50 rounded-lg">
                        <XCircle className="w-8 h-8 text-red-600" />
                        <div>
                          <p className="text-2xl font-bold text-red-900">{result.failed}</p>
                          <p className="text-sm text-red-700">Failed</p>
                        </div>
                      </div>
                    </div>

                    {result.errors.length > 0 && (
                      <div className="border border-red-200 bg-red-50 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                          <div className="flex-1">
                            <p className="font-medium text-red-900 mb-2">Errors:</p>
                            <ul className="space-y-1">
                              {result.errors.map((error, index) => (
                                <li key={index} className="text-sm text-red-700">
                                  • {error}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Instructions */}
            <Card>
              <CardHeader>
                <CardTitle>Instructions</CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 text-sm text-gray-700">
                  <li className="flex gap-3">
                    <span className="font-semibold text-primary-600">1.</span>
                    <span>Download the template using the button on the left</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="font-semibold text-primary-600">2.</span>
                    <span>Fill in your data following the exact column format</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="font-semibold text-primary-600">3.</span>
                    <span>Save as CSV or Excel file</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="font-semibold text-primary-600">4.</span>
                    <span>Upload using drag-and-drop or choose file button</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="font-semibold text-primary-600">5.</span>
                    <span>Review results and fix any errors if needed</span>
                  </li>
                </ol>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};