import { Sparkles } from "lucide-react";

const TypingIndicator = () => (
  <div className="flex gap-3 animate-fade-in" data-testid="typing-indicator">
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground shadow-glow">
      <Sparkles className="h-4 w-4" />
    </div>
    <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-md bg-card/80 backdrop-blur border border-border/60 px-4 py-3 shadow-soft">
      <span className="h-2 w-2 rounded-full bg-primary/60 animate-pulse-dot" />
      <span className="h-2 w-2 rounded-full bg-primary/60 animate-pulse-dot [animation-delay:0.2s]" />
      <span className="h-2 w-2 rounded-full bg-primary/60 animate-pulse-dot [animation-delay:0.4s]" />
    </div>
  </div>
);

export default TypingIndicator;
