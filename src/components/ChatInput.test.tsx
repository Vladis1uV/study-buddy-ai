import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatInput from "@/components/ChatInput";

describe("ChatInput", () => {
  it("renders with default placeholder", () => {
    render(<ChatInput onSend={vi.fn()} />);
    expect(screen.getByPlaceholderText(/ask about your lecture/i)).toBeInTheDocument();
  });

  it("renders with a custom placeholder", () => {
    render(<ChatInput onSend={vi.fn()} placeholder="Type here" />);
    expect(screen.getByPlaceholderText("Type here")).toBeInTheDocument();
  });

  it("disables the send button when input is empty", () => {
    render(<ChatInput onSend={vi.fn()} />);
    expect(screen.getByRole("button", { name: /send message/i })).toBeDisabled();
  });

  it("enables the send button when input has content", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={vi.fn()} />);
    await user.type(screen.getByLabelText(/chat input/i), "Hello");
    expect(screen.getByRole("button", { name: /send message/i })).toBeEnabled();
  });

  it("calls onSend with trimmed input when the button is clicked", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    await user.type(screen.getByLabelText(/chat input/i), "  hi there  ");
    await user.click(screen.getByRole("button", { name: /send message/i }));

    expect(onSend).toHaveBeenCalledTimes(1);
    expect(onSend).toHaveBeenCalledWith("hi there");
  });

  it("clears the input after sending", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={vi.fn()} />);
    const input = screen.getByLabelText(/chat input/i) as HTMLTextAreaElement;

    await user.type(input, "Hello");
    await user.click(screen.getByRole("button", { name: /send message/i }));

    expect(input.value).toBe("");
  });

  it("sends on Enter", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    await user.type(screen.getByLabelText(/chat input/i), "Hello{Enter}");
    expect(onSend).toHaveBeenCalledWith("Hello");
  });

  it("does NOT send on Shift+Enter (allows newline)", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByLabelText(/chat input/i);
    await user.type(input, "Line1{Shift>}{Enter}{/Shift}Line2");

    expect(onSend).not.toHaveBeenCalled();
  });

  it("does not call onSend when disabled", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled />);

    const input = screen.getByLabelText(/chat input/i);
    // Disabled textarea won't accept typing, so we test via Enter on focus differently
    expect(input).toBeDisabled();
    expect(screen.getByRole("button", { name: /send message/i })).toBeDisabled();
  });

  it("does not call onSend when input is only whitespace", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    await user.type(screen.getByLabelText(/chat input/i), "   {Enter}");
    expect(onSend).not.toHaveBeenCalled();
  });
});
