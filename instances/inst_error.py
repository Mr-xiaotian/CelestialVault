class DownloadError(Exception):
    """Raised when the download process fails."""
    pass


class FFmpegError(DownloadError):
    """Raised when FFmpeg execution fails."""
    def __init__(self, message, stderr=None):
        super().__init__(message)
        self.stderr = stderr