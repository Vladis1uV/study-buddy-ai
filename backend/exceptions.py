
class StudyBuddyError(Exception):
    status_code: int = 500
    public_message: str = "An internal error occurred."


class DocumentNotFoundError(StudyBuddyError):
    status_code = 404
    public_message = "Document not found. It may have expired — please upload it again."


class EmptyDocumentError(StudyBuddyError):
    status_code = 422
    public_message = "Document appears to be empty or unreadable."


class UnsupportedFormatError(StudyBuddyError):
    status_code = 415
    public_message = "Unsupported file format. Please upload PDF or DOCX."


class DocumentParsingError(StudyBuddyError):
    status_code = 422
    public_message = "Failed to read the document. The file may be corrupted."


class FileTooLargeError(StudyBuddyError):
    status_code = 413
    public_message = "File too large. Maximum size is 10 MB."


class LLMUpstreamError(StudyBuddyError):
    status_code = 502
    public_message = "The language model service is unavailable. Please try again."


class LLMTimeoutError(LLMUpstreamError):
    status_code = 504
    public_message = "The language model service timed out. Please try again."
