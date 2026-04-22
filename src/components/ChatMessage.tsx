import { Sparkles, User } from "lucide-react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-3 animate-fade-in ${isUser ? "flex-row-reverse" : ""}`}
      data-testid={`message-${message.role}`}
    >
      <div
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
          isUser
            ? "bg-secondary text-secondary-foreground"
            : "bg-gradient-primary text-primary-foreground shadow-glow"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
      </div>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-gradient-primary text-primary-foreground rounded-tr-md shadow-soft"
            : "bg-card/80 backdrop-blur border border-border/60 rounded-tl-md shadow-soft"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
};

export default ChatMessage;
