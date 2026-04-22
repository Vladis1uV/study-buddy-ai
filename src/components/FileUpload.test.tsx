import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import FileUpload from "@/components/FileUpload";

const API = "http://test-api";

describe("FileUpload", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the dropzone prompt initially", () => {
    render(<FileUpload onFileUploaded={vi.fn()} apiBaseUrl={API} />);
    expect(screen.getByText(/drop your lecture notes here/i)).toBeInTheDocument();
    expect(screen.getByText(/pdf and docx supported/i)).toBeInTheDocument();
  });

  it("uploads a selected file and calls onFileUploaded with the document id", async () => {
    const user = userEvent.setup();
    const onFileUploaded = vi.fn();
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ document_id: "doc-123" }),
    });

    const { container } = render(
      <FileUpload onFileUploaded={onFileUploaded} apiBaseUrl={API} />,
    );
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["hello"], "notes.pdf", { type: "application/pdf" });

    await user.upload(fileInput, file);

    await waitFor(() => {
      expect(onFileUploaded).toHaveBeenCalledTimes(1);
    });
    expect(onFileUploaded).toHaveBeenCalledWith(file, "doc-123");
    expect(global.fetch).toHaveBeenCalledWith(
      `${API}/api/upload`,
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders the success state with the file name after upload", async () => {
    const user = userEvent.setup();
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ document_id: "doc-1" }),
    });

    const { container } = render(
      <FileUpload onFileUploaded={vi.fn()} apiBaseUrl={API} />,
    );
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(fileInput, new File(["x"], "lecture.pdf", { type: "application/pdf" }));

    expect(await screen.findByText("lecture.pdf")).toBeInTheDocument();
  });

  it("shows an error message when the upload fails", async () => {
    const user = userEvent.setup();
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
    });

    const { container } = render(
      <FileUpload onFileUploaded={vi.fn()} apiBaseUrl={API} />,
    );
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(fileInput, new File(["x"], "bad.pdf", { type: "application/pdf" }));

    expect(await screen.findByText(/failed to upload file/i)).toBeInTheDocument();
  });

  it("shows an error message when fetch throws (network error)", async () => {
    const user = userEvent.setup();
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("network"));

    const { container } = render(
      <FileUpload onFileUploaded={vi.fn()} apiBaseUrl={API} />,
    );
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(fileInput, new File(["x"], "n.pdf", { type: "application/pdf" }));

    expect(await screen.findByText(/failed to upload file/i)).toBeInTheDocument();
  });
});
