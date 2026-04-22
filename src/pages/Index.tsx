import { useState, useRef, useEffect } from "react";
import { Sparkles, Settings, Github } from "lucide-react";
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
    <div className="flex h-screen flex-col bg-gradient-mesh">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border/60 bg-background/70 backdrop-blur-xl px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight tracking-tight">
              Study Assistant
            </h1>
            <p className="text-xs text-muted-foreground">RAG-powered lecture Q&A</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-9 w-9 rounded-lg" asChild>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
              <Github className="h-4 w-4" />
            </a>
          </Button>
          <Button variant="ghost" size="icon" className="h-9 w-9 rounded-lg" aria-label="Settings">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {!documentId ? (
          /* Upload state */
          <div className="flex flex-1 items-center justify-center p-6">
            <div className="w-full max-w-lg space-y-8 animate-fade-in">
              <div className="text-center space-y-3">
                <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-background/60 backdrop-blur px-3 py-1 text-xs font-medium text-muted-foreground shadow-soft">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse-dot" />
                  Powered by RAG
                </div>
                <h2 className="text-4xl font-bold tracking-tight">
                  Turn lectures into{" "}
                  <span className="text-gradient-primary">conversations</span>
                </h2>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  Upload your notes and chat with them. Grounded answers, instantly.
                </p>
              </div>

              <div className="rounded-2xl border border-border/60 bg-card/70 backdrop-blur-xl p-6 shadow-elevated">
                <FileUpload onFileUploaded={handleFileUploaded} apiBaseUrl={API_BASE_URL} />
              </div>

              <div className="grid grid-cols-2 gap-3">
                {[
                  { step: "01", text: "Upload notes" },
                  { step: "02", text: "Auto-embed" },
                  { step: "03", text: "Ask anything" },
                  { step: "04", text: "Grounded answers" },
                ].map((item) => (
                  <div
                    key={item.step}
                    className="rounded-xl border border-border/60 bg-card/50 backdrop-blur p-3"
                  >
                    <div className="text-[10px] font-mono font-semibold text-primary">
                      {item.step}
                    </div>
                    <div className="text-sm font-medium mt-0.5">{item.text}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Chat state */
          <>
            {/* Active document bar */}
            <div className="flex items-center gap-2 border-b border-border/60 bg-background/60 backdrop-blur-xl px-6 py-2.5">
              <span className="h-2 w-2 rounded-full bg-success animate-pulse-dot" />
              <span className="text-xs text-muted-foreground">Active document:</span>
              <span className="text-xs font-medium truncate">{fileName}</span>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-8 space-y-4">
              <div className="mx-auto max-w-3xl space-y-4">
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
                {isLoading && <TypingIndicator />}
              </div>
            </div>

            {/* Input */}
            <div className="border-t border-border/60 bg-background/70 backdrop-blur-xl p-4">
              <div className="mx-auto max-w-3xl">
                <ChatInput onSend={handleSend} disabled={isLoading} />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Index;
