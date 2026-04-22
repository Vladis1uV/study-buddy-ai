import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ChatMessage, { Message } from "@/components/ChatMessage";

const makeMessage = (overrides: Partial<Message> = {}): Message => ({
  id: "m1",
  role: "assistant",
  content: "Hello world",
  timestamp: new Date(),
  ...overrides,
});

describe("ChatMessage", () => {
  it("renders the message content", () => {
    render(<ChatMessage message={makeMessage({ content: "Some answer" })} />);
    expect(screen.getByText("Some answer")).toBeInTheDocument();
  });

  it("uses the assistant variant for assistant messages", () => {
    render(<ChatMessage message={makeMessage({ role: "assistant" })} />);
    expect(screen.getByTestId("message-assistant")).toBeInTheDocument();
  });

  it("uses the user variant for user messages", () => {
    render(<ChatMessage message={makeMessage({ role: "user", content: "My question" })} />);
    expect(screen.getByTestId("message-user")).toBeInTheDocument();
    expect(screen.getByText("My question")).toBeInTheDocument();
  });

  it("renders user messages reversed (avatar on the right)", () => {
    render(<ChatMessage message={makeMessage({ role: "user" })} />);
    const wrapper = screen.getByTestId("message-user");
    expect(wrapper.className).toContain("flex-row-reverse");
  });

  it("does NOT reverse assistant messages", () => {
    render(<ChatMessage message={makeMessage({ role: "assistant" })} />);
    const wrapper = screen.getByTestId("message-assistant");
    expect(wrapper.className).not.toContain("flex-row-reverse");
  });
});
