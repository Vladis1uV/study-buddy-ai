import { useCallback, useRef, useState } from "react";
import { Upload, FileText, Download, RefreshCw } from "lucide-react";
import { marked } from "marked";
import html2pdf from "html2pdf.js";
import { Button } from "@/components/ui/button";

interface SummarizePanelProps {
  apiBaseUrl: string;
}

interface SummaryResult {
  summaryMarkdown: string;
  originalFilename: string;
}

const stripExtension = (name: string) => name.replace(/\.[^.]+$/, "");

const SummarizePanel = ({ apiBaseUrl }: SummarizePanelProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SummaryResult | null>(null);
  const summaryRef = useRef<HTMLDivElement>(null);

  const summarize = async (file: File) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${apiBaseUrl}/api/summarize`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let detail = "Summarization failed.";
        try {
          const body = await res.json();
          if (body?.detail) detail = body.detail;
        } catch {
          // non-JSON error body — keep the default
        }
        throw new Error(detail);
      }

      const data = await res.json();
      setResult({
        summaryMarkdown: data.summary_markdown,
        originalFilename: data.original_filename,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) summarize(file);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) summarize(file);
  };

  const downloadPdf = async () => {
    if (!summaryRef.current || !result) return;
    const filename = `${stripExtension(result.originalFilename)}-summary.pdf`;
    await html2pdf()
      .set({
        margin: 15,
        filename,
        image: { type: "jpeg", quality: 0.95 },
        html2canvas: { scale: 2, backgroundColor: "#ffffff" },
        jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
      })
      .from(summaryRef.current)
      .save();
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  if (result) {
    const html = marked.parse(result.summaryMarkdown, { async: false }) as string;

    return (
      <div className="space-y-4 animate-fade-in">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <FileText className="h-4 w-4 text-primary" />
            <span className="truncate font-medium">{result.originalFilename}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={reset} aria-label="Summarize another">
              <RefreshCw className="h-4 w-4 mr-1.5" />
              New
            </Button>
            <Button size="sm" onClick={downloadPdf} aria-label="Download PDF">
              <Download className="h-4 w-4 mr-1.5" />
              Download PDF
            </Button>
          </div>
        </div>

        {/* Rendered summary — also the source for the PDF export */}
        <div
          ref={summaryRef}
          data-testid="summary-content"
          className="rounded-2xl border border-border/60 bg-card/80 backdrop-blur-xl p-6 shadow-soft"
        >
          <h2 className="text-lg font-semibold mb-3">Summary</h2>
          <div
            className="prose prose-sm max-w-none text-foreground leading-relaxed"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        </div>
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
          aria-label="Upload file to summarize"
          className="absolute inset-0 opacity-0 cursor-pointer"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          disabled={isLoading}
        />
        <Upload className={`h-8 w-8 text-muted-foreground ${isLoading ? "animate-pulse" : ""}`} />
        <div className="text-center">
          <p className="text-sm font-medium">
            {isLoading ? "Summarizing..." : "Drop your lecture or homework here"}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            We'll return a ~500 word TL;DR you can download as PDF.
          </p>
        </div>
      </div>
      {error && <p className="text-xs text-destructive mt-2 animate-fade-in">{error}</p>}
    </div>
  );
};

export default SummarizePanel;
