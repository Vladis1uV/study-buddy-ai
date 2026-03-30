import { useState, useRef, useEffect } from "react";
import { BookOpen, Settings, Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import FileUpload from "@/components/FileUpload";
import ChatMessage, { Message } from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import TypingIndicator from "@/components/TypingIndicator";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const Index = () => {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  const handleFileUploaded = (file: File, docId: string) => {
    setDocumentId(docId);
    setFileName(file.name);
    setMessages([
      {
        id: "system-1",
        role: "assistant",
        content: `I've processed "${file.name}". Ask me anything about this document!`,
        timestamp: new Date(),
      },
    ]);
  };

  const handleSend = async (content: string) => {
    if (!documentId) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: documentId, question: content }),
      });

      if (!res.ok) throw new Error("Request failed");

      const data = await res.json();
      const assistantMsg: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I couldn't reach the backend. Make sure it's running on " + API_BASE_URL,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight">Study Assistant</h1>
            <p className="text-xs text-muted-foreground">RAG-powered lecture Q&A</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              <Github className="h-4 w-4" />
            </a>
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {!documentId ? (
          /* Upload state */
          <div className="flex flex-1 items-center justify-center p-6">
            <div className="w-full max-w-md space-y-6 animate-fade-in">
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-semibold">Upload your notes</h2>
                <p className="text-sm text-muted-foreground">
                  Upload a lecture file and I'll answer your questions using RAG
                </p>
              </div>
              <FileUpload onFileUploaded={handleFileUploaded} apiBaseUrl={API_BASE_URL} />
              <div className="flex items-center gap-3 rounded-lg bg-accent/50 border border-border p-3">
                <div className="text-xs text-muted-foreground space-y-1">
                  <p className="font-medium text-accent-foreground">How it works:</p>
                  <p>1. Upload your lecture notes (PDF, TXT, MD, DOCX)</p>
                  <p>2. The backend chunks & embeds your document</p>
                  <p>3. Ask questions — RAG retrieves relevant context</p>
                  <p>4. LLM generates answers grounded in your notes</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Chat state */
          <>
            {/* Active document bar */}
            <div className="flex items-center gap-2 border-b border-border bg-accent/30 px-6 py-2">
              <span className="text-xs text-muted-foreground">Active document:</span>
              <span className="text-xs font-medium">{fileName}</span>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              {isLoading && <TypingIndicator />}
            </div>

            {/* Input */}
            <div className="border-t border-border p-4">
              <ChatInput onSend={handleSend} disabled={isLoading} />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Index;
