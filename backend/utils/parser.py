import io
from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse(self, content: bytes) -> str:
        pass


class PDFParser(Parser):
    def parse(self, content: bytes) -> str:
        import pdfplumber

        text = ""

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        return text


class DOCXParser(Parser):
    def parse(self, content: bytes) -> str:
        import docx

        doc = docx.Document(io.BytesIO(content))
        text = ""

        for page in doc.paragraphs:
            text += page.text + "\n"

        return text


class ParserFactory:
    @staticmethod
    def get_parser(content: bytes) -> Parser:
        if content.startswith(b"%PDF"):
            return PDFParser()
        elif content.startswith(b"PK\x03\x04"):
            return DOCXParser()
        else:
            raise ValueError("Unsupported file format")
