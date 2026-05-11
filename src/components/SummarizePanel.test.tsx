import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SummarizePanel from "@/components/SummarizePanel";

const API = "http://test-api";

const { chain, mockSave } = vi.hoisted(() => {
  const save = vi.fn().mockResolvedValue(undefined);
  const c: { set: ReturnType<typeof vi.fn>; from: ReturnType<typeof vi.fn>; save: typeof save } = {
    set: vi.fn(),
    from: vi.fn(),
    save,
  };
  c.set.mockReturnValue(c);
  c.from.mockReturnValue(c);
  return { chain: c, mockSave: save };
});

vi.mock("html2pdf.js", () => ({
  default: () => chain,
}));

const uploadFileTo = async (filename: string) => {
  const user = userEvent.setup();
  const { container } = render(<SummarizePanel apiBaseUrl={API} />);
  const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
  await user.upload(
    fileInput,
    new File(["x"], filename, { type: "application/pdf" }),
  );
  return user;
};

describe("SummarizePanel", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    chain.set.mockReset().mockReturnValue(chain);
    chain.from.mockReset().mockReturnValue(chain);
    mockSave.mockReset().mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the dropzone prompt initially", () => {
    render(<SummarizePanel apiBaseUrl={API} />);
    expect(screen.getByText(/drop your lecture or homework here/i)).toBeInTheDocument();
    expect(screen.getByText(/500 word/i)).toBeInTheDocument();
  });

  it("posts the file to /api/summarize and renders the returned markdown", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        summary_markdown: "This **is** the summary.",
        original_filename: "lecture.pdf",
      }),
    });

    await uploadFileTo("lecture.pdf");

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${API}/api/summarize`,
        expect.objectContaining({ method: "POST" }),
      );
    });

    const summary = await screen.findByTestId("summary-content");
    // marked renders **is** as <strong>
    expect(summary.innerHTML).toContain("<strong>is</strong>");
    expect(screen.getByText("lecture.pdf")).toBeInTheDocument();
  });

  it("shows the backend's error detail when /api/summarize fails", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Unsupported file format." }),
    });

    await uploadFileTo("bad.pdf");

    expect(await screen.findByText(/unsupported file format/i)).toBeInTheDocument();
  });

  it("shows a generic error when fetch throws", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("network"));

    await uploadFileTo("n.pdf");

    expect(await screen.findByText(/network/i)).toBeInTheDocument();
  });

  it("triggers the html2pdf save() chain when Download PDF is clicked", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        summary_markdown: "Body.",
        original_filename: "lecture.pdf",
      }),
    });

    const user = await uploadFileTo("lecture.pdf");
    const downloadBtn = await screen.findByRole("button", { name: /download pdf/i });
    await user.click(downloadBtn);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledTimes(1);
    });
    // filename derived from original_filename minus extension
    const setCallArgs = chain.set.mock.calls[0][0];
    expect(setCallArgs.filename).toBe("lecture-summary.pdf");
  });

  it("resets back to the dropzone when New is clicked", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        summary_markdown: "Body.",
        original_filename: "lecture.pdf",
      }),
    });

    const user = await uploadFileTo("lecture.pdf");
    const newBtn = await screen.findByRole("button", { name: /summarize another/i });
    await user.click(newBtn);

    expect(screen.getByText(/drop your lecture or homework here/i)).toBeInTheDocument();
  });
});
