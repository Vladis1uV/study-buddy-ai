from backend.rag.chunker import DocumentChunker


def test_empty_text_returns_no_chunks():
    chunker = DocumentChunker()
    assert chunker.chunk("") == []


def test_short_text_returns_single_chunk():
    chunker = DocumentChunker()
    text = "Hello world"
    chunks = chunker.chunk(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_produces_multiple_chunks():
    # chunk_size=50, overlap=10 → step=40
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    text = "a" * 200
    chunks = chunker.chunk(text)
    assert len(chunks) > 1


def test_chunks_respect_chunk_size():
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    text = "a" * 200
    for chunk in chunker.chunk(text):
        assert len(chunk) <= 50


def test_consecutive_chunks_overlap():
    # With chunk_size=10 and overlap=4, step=6
    # chunk 0: text[0:10], chunk 1: text[6:16] — they share text[6:10]
    chunker = DocumentChunker(chunk_size=10, chunk_overlap=4)
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunker.chunk(text)
    assert len(chunks) >= 2
    # Last 4 chars of chunk 0 should equal first 4 chars of chunk 1
    assert chunks[0][-4:] == chunks[1][:4]
