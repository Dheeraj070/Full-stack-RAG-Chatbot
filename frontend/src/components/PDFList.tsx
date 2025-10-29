import React from 'react'
import { PDFDocument } from '@/types'
import { formatFileSize } from '@/utils/helpers'
import { X, FileText } from 'lucide-react'

interface PDFListProps {
  pdfs: PDFDocument[]
  onDelete: (pdfId: string) => void
}

const PDFList: React.FC<PDFListProps> = ({ pdfs, onDelete }) => {
  if (pdfs.length === 0) {
    return <p className="text-xs text-gray-500 text-center py-4">No PDFs uploaded yet</p>
  }

  return (
    <>
      {pdfs.map((pdf) => (
        <div
          key={pdf.id}
          className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200"
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate">{pdf.filename}</p>
              <p className="text-xs text-gray-500">
                {formatFileSize(pdf.file_size)} • {pdf.page_count} pages
              </p>
            </div>
          </div>
          <button
            onClick={() => onDelete(pdf.id)}
            className="ml-2 p-1 text-red-600 hover:text-red-700 transition-colors flex-shrink-0"
            title="Delete PDF"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </>
  )
}

export default PDFList