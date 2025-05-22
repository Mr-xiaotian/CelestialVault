from datetime import datetime


def format_duration(seconds):
    """将秒数格式化为 HH:MM:SS 或 MM:SS（自动省略前导零）"""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_timestamp(timestamp) -> str:
    """将时间戳格式化为 YYYY-MM-DD HH:MM:SS"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')