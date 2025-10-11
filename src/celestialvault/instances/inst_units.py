import re

class HumanBytes(int):
    """一个基于 int 的类，自动以人类可读格式显示字节大小"""

    _units = ["B", "KB", "MB", "GB", "TB"]
    _unit_map = {u: 1024 ** i for i, u in enumerate(_units)}

    def __new__(cls, value):
        """允许用数字或字符串初始化"""
        if isinstance(value, str):
            value = cls._parse_human(value)
        return super().__new__(cls, int(value))

    # -------------------------
    # 🧮 转换与解析
    # -------------------------
    @classmethod
    def _parse_human(cls, text: str) -> int:
        """解析 '1GB 512MB' 或 '1.5 GB'"""
        size_in_bytes = 0

        matches = re.findall(r"(\d+(?:\.\d+)?)([A-Za-z]+)", text)
        if not matches:
            raise ValueError(f"无法解析输入: {text}")

        for value, unit in matches:
            unit = unit.upper()
            if unit not in cls._unit_map:
                raise ValueError(f"未知单位: {unit}")
            size_in_bytes += float(value) * cls._unit_map[unit]

        return int(size_in_bytes)

    def _to_human(self) -> str:
        """转换为人类可读字符串"""
        if int(self) <= 0:
            return "0B"

        result = []

        for unit in reversed(self._units):
            unit_size = 1024 ** self._units.index(unit)
            if int(self) >= unit_size:
                value = int(self) // unit_size
                self %= unit_size
                result.append(f"{value}{unit}")

        return " ".join(result)

    # -------------------------
    # 🎨 显示与表示
    # -------------------------
    def __str__(self):
        return self._to_human()

    def __repr__(self):
        return f"HumanBytes({int(self)} -> {self._to_human()})"

    # -------------------------
    # 🔄 运算保持类型
    # -------------------------
    def _wrap(self, result):
        return HumanBytes(result)

    def __add__(self, other): return self._wrap(super().__add__(other))
    def __sub__(self, other): return self._wrap(super().__sub__(other))
    def __mul__(self, other): return self._wrap(super().__mul__(other))
    def __floordiv__(self, other): return self._wrap(super().__floordiv__(other))
    def __truediv__(self, other): return self._wrap(super().__truediv__(other))
    def __mod__(self, other): return self._wrap(super().__mod__(other))
