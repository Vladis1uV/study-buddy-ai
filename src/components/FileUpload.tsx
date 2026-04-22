import { useState, useCallback } from "react";
import { Upload, FileText, X, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FileUploadProps {
  onFileUploaded: (file: File, documentId: string) => void;
  apiBaseUrl: string;
}

const FileUpload = ({ onFileUploaded, apiBaseUrl }: FileUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${apiBaseUrl}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setUploadedFile(file);
      onFileUploaded(file, data.document_id);
    } catch (err) {
      setError("Failed to upload file. Is the backend running?");
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setUploadedFile(null);
    setError(null);
  };

  if (uploadedFile) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-border bg-accent/50 p-3 animate-fade-in">
        <CheckCircle className="h-5 w-5 text-success shrink-0" />
        <FileText className="h-5 w-5 text-primary shrink-0" />
        <span className="text-sm font-medium truncate flex-1">
          {uploadedFile.name}
        </span>
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={clearFile}>
          <X className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 transition-colors cursor-pointer ${
          isDragging
            ? "border-primary bg-accent"
            : "border-border hover:border-primary/50 hover:bg-accent/30"
        }`}
      >
        <input
          type="file"
          className="absolute inset-0 opacity-0 cursor-pointer"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          disabled={uploading}
        />
        <Upload className={`h-8 w-8 text-muted-foreground ${uploading ? "animate-pulse" : ""}`} />
        <div className="text-center">
          <p className="text-sm font-medium">
            {uploading ? "Uploading..." : "Drop your lecture notes here"}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            PDF and DOCX supported
          </p>
        </div>
      </div>
      {error && (
        <p className="text-xs text-destructive mt-2 animate-fade-in">{error}</p>
      )}
    </div>
  );
};

export default FileUpload;
