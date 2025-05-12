from tqdm import tqdm
from tqdm.asyncio import tqdm as tqdm_asy


class ProgressManager:
    def __init__(
        self,
        total_tasks: int,
        desc: str = "Processing",
        mode: str = "normal",
        show_progress: bool = False,
    ):
        """
        初始化进度条管理器

        :param total_tasks: 任务总数，用于设置进度条的总长度
        :param desc: 进度条的描述文字
        :param mode: 任务模式，可选 "async", other
        :param show_progress: 是否显示进度条
        """
        if show_progress:
            if mode == "async":
                self.progress_bar = tqdm_asy(total=total_tasks, desc=desc)
            else:
                self.progress_bar = tqdm(total=total_tasks, desc=desc)
        else:
            self.progress_bar = None
        self.show_progress = show_progress

    def update(self, n=1):
        """更新进度条"""
        if self.show_progress and self.progress_bar:
            self.progress_bar.update(n)

    def close(self):
        """关闭进度条"""
        if self.show_progress and self.progress_bar:
            self.progress_bar.close()

    def refresh_total(self, total):
        """动态调整进度条的总任务数"""
        if self.show_progress and self.progress_bar:
            self.progress_bar.total = total
            self.progress_bar.refresh()

    def add_total(self, add_num):
        """动态增加进度条的总任务数"""
        total = self.progress_bar.total + add_num
        self.refresh_total(total)
