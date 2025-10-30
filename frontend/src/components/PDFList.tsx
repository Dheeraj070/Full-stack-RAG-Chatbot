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
          className="flex items-center justify-between p-2 bg-dark-hover rounded-lg border border-dark-border hover:border-cyan-400/50 transition-all group"
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <div className="p-1.5 bg-cyan-400/10 rounded">
              <FileText className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-300 truncate">{pdf.filename}</p>
              <p className="text-xs text-gray-500">
                {formatFileSize(pdf.file_size)} • {pdf.page_count} pages
              </p>
            </div>
          </div>
          <button
            onClick={() => onDelete(pdf.id)}
            className="ml-2 p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-all opacity-0 group-hover:opacity-100 flex-shrink-0"
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