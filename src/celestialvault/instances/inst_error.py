class DownloadError(Exception):
    """Raised when the download process fails."""

    pass


class FFmpegError(DownloadError):
    """Raised when FFmpeg execution fails."""

    def __init__(self, message, stderr=None):
        """
        初始化 FFmpeg 错误。

        :param message: 错误信息。
        :param stderr: FFmpeg 的标准错误输出。
        """
        super().__init__(message)
        self.stderr = stderr
