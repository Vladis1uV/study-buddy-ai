import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import TypingIndicator from "@/components/TypingIndicator";

describe("TypingIndicator", () => {
  it("renders the indicator", () => {
    render(<TypingIndicator />);
    expect(screen.getByTestId("typing-indicator")).toBeInTheDocument();
  });

  it("renders three animated dots", () => {
    render(<TypingIndicator />);
    const indicator = screen.getByTestId("typing-indicator");
    const dots = indicator.querySelectorAll(".animate-pulse-dot");
    expect(dots).toHaveLength(3);
  });
});
