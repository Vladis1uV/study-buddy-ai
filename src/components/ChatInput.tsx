import { useState } from "react";
import { ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput = ({ onSend, disabled, placeholder = "Ask about your lecture..." }: ChatInputProps) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  return (
    <div className="relative flex items-end gap-2 rounded-2xl border border-border/60 bg-card/80 backdrop-blur-xl p-2 shadow-soft focus-within:border-primary/50 focus-within:shadow-glow transition-all">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        aria-label="Chat input"
        className="flex-1 resize-none bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none disabled:opacity-50"
      />
      <Button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        size="icon"
        aria-label="Send message"
        className="h-9 w-9 shrink-0 rounded-xl bg-gradient-primary hover:opacity-90 shadow-glow"
      >
        <ArrowUp className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default ChatInput;
