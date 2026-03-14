import React, { useState } from 'react';
import { FileDown, FileSpreadsheet, FileText } from 'lucide-react';
import { Button } from './Button';
import toast from 'react-hot-toast';

interface ExportButtonProps {
  onExportPDF: () => Promise<Blob>;
  onExportExcel: () => Promise<Blob>;
  pdfFilename: string;
  excelFilename: string;
  label?: string;
}

export const ExportButton: React.FC<ExportButtonProps> = ({
  onExportPDF,
  onExportExcel,
  pdfFilename,
  excelFilename,
  label = 'Export',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format: 'pdf' | 'excel') => {
    setExporting(true);
    setIsOpen(false);

    try {
      const blob = format === 'pdf' ? await onExportPDF() : await onExportExcel();
      const filename = format === 'pdf' ? pdfFilename : excelFilename;

      // Download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success(`${format.toUpperCase()} exported successfully!`);
    } catch (error: any) {
      console.error('Export error:', error);
      toast.error(error.response?.data?.detail || 'Failed to export');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="relative">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="outline"
        loading={exporting}
        disabled={exporting}
      >
        <FileDown className="w-4 h-4" />
        {label}
      </Button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            <div className="py-1">
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center gap-3 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <FileText className="w-4 h-4 text-red-600" />
                <span>Export as PDF</span>
              </button>
              <button
                onClick={() => handleExport('excel')}
                className="flex items-center gap-3 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <FileSpreadsheet className="w-4 h-4 text-green-600" />
                <span>Export as Excel</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};