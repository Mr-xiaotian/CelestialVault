import time
from pathlib import Path

from celestialflow import TaskExecutor, TaskProgress

from celestialvault.tools.FileOperations import (
    get_file_info,
)


def scan(dir_path: Path, max_workers) -> dict:
    scan_info_executor = TaskExecutor(
        "Scanning files",
        get_file_info,
        "thread",
        max_workers=max_workers,
    )
    scan_info_executor.add_observer(TaskProgress())

    file_path_list = [
        file_path for file_path in dir_path.glob("**/*") if file_path.is_file()
    ]
    start_time = time.perf_counter()
    scan_info_executor.start(file_path_list)
    end_time = time.perf_counter()
    print(f"Scanning completed in {end_time - start_time:.2f} seconds")


def main():
    dir_path = Path(r"Q:\Project\CelestialFlow")

    for max_workers in [1, 2, 4, 8, 16]:
        print(f"Scanning with max_workers={max_workers}...")
        scan(dir_path, max_workers=max_workers)


if __name__ == "__main__":
    main()
