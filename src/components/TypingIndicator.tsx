import { Bot } from "lucide-react";

const TypingIndicator = () => (
  <div className="flex gap-3 animate-fade-in">
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
      <Bot className="h-4 w-4" />
    </div>
    <div className="flex items-center gap-1.5 rounded-xl bg-card border border-border px-4 py-3 rounded-tl-sm">
      <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot" />
      <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot [animation-delay:0.2s]" />
      <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot [animation-delay:0.4s]" />
    </div>
  </div>
);

export default TypingIndicator;
