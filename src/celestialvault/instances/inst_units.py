from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo


class HumanBytes(int):
    """一个基于 int 的类，自动以人类可读格式显示字节大小"""

    _units = ["B", "KB", "MB", "GB", "TB"]
    _unit_map = {u: 1024**i for i, u in enumerate(_units)}

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

    def __add__(self, other):
        return self._wrap(super().__add__(other))

    def __sub__(self, other):
        return self._wrap(super().__sub__(other))

    def __mul__(self, other):
        return self._wrap(super().__mul__(other))

    def __floordiv__(self, other):
        return self._wrap(super().__floordiv__(other))

    def __truediv__(self, other):
        return self._wrap(super().__truediv__(other))

    def __mod__(self, other):
        return self._wrap(super().__mod__(other))


class HumanTime(float):
    """
    表示可读的时间长度（duration），单位为秒（float）。
    - 运算行为与 float 一致，可加减乘除
    - 打印时自动格式化为 1d 2h 3m 4.56s 形式
    - 支持从字符串初始化，如 "1d 2h 3m 4.56s"
    """

    _units = [
        ("d", 86400),
        ("h", 3600),
        ("m", 60),
        ("s", 1),
    ]

    def __new__(cls, value: str | float | int):
        if isinstance(value, str):
            value = cls._parse_human(value)
        return super().__new__(cls, float(value))

    # -------------------------
    # 🔁 解析字符串 → 秒数
    # -------------------------
    @classmethod
    def _parse_human(cls, text: str) -> float:
        """解析 '1d 2h 3m 4s' 形式的字符串"""
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*([dhms])", text, flags=re.I)
        if not matches:
            raise ValueError(f"无法解析时间长度: {text}")
        total = 0.0
        for val, unit in matches:
            val = float(val)
            unit = unit.lower()
            for u, factor in cls._units:
                if u == unit:
                    total += val * factor
                    break
            else:
                raise ValueError(f"未知单位: {unit}")
        return total

    # -------------------------
    # 🔁 秒数 → 人类可读字符串
    # -------------------------
    def _to_human(self, precision=2, show_zero=False) -> str:
        """格式化为如 '1d 2h 3m 4.56s' 的字符串"""
        remaining = abs(float(self))
        parts = []
        for unit, factor in self._units:
            if remaining >= factor or (show_zero and parts):
                val = int(remaining // factor)
                remaining -= val * factor
                if val or show_zero:
                    parts.append(f"{val}{unit}")
        # 小数秒
        if remaining > 0:
            parts.append(f"{remaining:.{precision}f}s")
        if not parts:
            parts = ["0s"]
        sign = "-" if self < 0 else ""
        return sign + " ".join(parts)

    # -------------------------
    # 🎨 显示与调试
    # -------------------------
    def __str__(self):
        return self._to_human()

    def __repr__(self):
        return f"HumanTime({float(self):.6f}s -> {self._to_human()})"

    # -------------------------
    # 🔄 运算保持类型
    # -------------------------
    def _wrap(self, result):
        return HumanTime(result)

    def __add__(self, other):
        return self._wrap(super().__add__(other))

    def __sub__(self, other):
        return self._wrap(super().__sub__(other))

    def __mul__(self, other):
        return self._wrap(super().__mul__(other))

    def __truediv__(self, other):
        return self._wrap(super().__truediv__(other))

    def __floordiv__(self, other):
        return self._wrap(super().__floordiv__(other))

    def __radd__(self, other):
        return self._wrap(super().__radd__(other))

    def __rsub__(self, other):
        return self._wrap(super().__rsub__(other))

    def __rmul__(self, other):
        return self._wrap(super().__rmul__(other))


class HumanTimestamp(float):
    """
    基于 float 的 UNIX 时间戳（单位：秒，支持小数）。
    - 显示（print/str）为人类可读的本地时间（含时区偏移）
    - 默认时区：Asia/Shanghai；可用 with_tz() 切换视图时区
    - 加/减『秒数』返回 HumanTimestamp；两个 HumanTimestamp 相减返回 HumanTime
    """

    DEFAULT_TZ = ZoneInfo("Asia/Shanghai")

    def __new__(cls, value: float | int | str | datetime, tz=None):
        tz = tz or cls.DEFAULT_TZ

        # ---- 数字类型 ----
        if isinstance(value, (int, float)):
            epoch = float(value)

        # ---- datetime 类型 ----
        elif isinstance(value, datetime):
            dt = value if value.tzinfo else value.replace(tzinfo=tz)
            epoch = dt.timestamp()

        # ---- 字符串 ----
        elif isinstance(value, str):
            s = value.strip()
            try:
                epoch = float(s)
            except ValueError:
                iso = s.replace(" ", "T", 1) if (" " in s and "T" not in s) else s
                try:
                    dt = datetime.fromisoformat(iso)
                except ValueError as e:
                    raise ValueError(f"无法解析为时间戳或 ISO 格式: {value!r}") from e
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=tz)
                epoch = dt.timestamp()
        else:
            raise TypeError(f"不支持的初始化类型: {type(value).__name__}")

        obj = super().__new__(cls, epoch)
        obj._tz = tz
        return obj

    # ---------- 时区与转换 ----------
    @property
    def tz(self):
        """
        返回当前对象的时区。

        :return: 时区对象。
        """
        return self._tz

    def with_tz(self, tz) -> HumanTimestamp:
        """返回一个仅改变显示时区的新对象（纪元秒不变）"""
        return HumanTimestamp(float(self), tz=tz)

    def to_datetime(self, tz=None) -> datetime:
        """
        将时间戳转换为 datetime 对象。

        :param tz: 目标时区，默认使用自身时区。
        :return: 对应的 datetime 对象。
        """
        tz = tz or self._tz
        return datetime.fromtimestamp(float(self), tz)

    def to_iso(self, tz=None, timespec: str = "milliseconds") -> str:
        """返回 ISO 8601 字符串（含偏移）"""
        return self.to_datetime(tz).isoformat(timespec=timespec)

    # ---------- 显示 ----------
    def __str__(self):
        dt = self.to_datetime()
        iso = dt.isoformat(timespec="milliseconds")  # 例：2025-03-25T12:49:22.104+09:00
        name = dt.tzname() or ""
        return f"{iso} ({name})" if name else iso

    def __repr__(self):
        tz_label = getattr(self._tz, "key", None) or (
            self._tz.tzname(None) if hasattr(self._tz, "tzname") else "tz"
        )
        return f"HumanTimestamp({float(self):.6f}, tz='{tz_label}') -> {self.to_iso()}"

    # ---------- 运算（尽量保持语义） ----------
    def _wrap(self, epoch: float) -> HumanTimestamp:
        return HumanTimestamp(epoch, tz=self._tz)

    # 加：时间戳 + 秒数 -> 新时间戳
    def __add__(self, other):
        if isinstance(other, (int, float, HumanTime)):
            return self._wrap(float(self) + float(other))
        if isinstance(other, HumanTimestamp):
            raise TypeError(
                "时间戳与时间戳相加没有语义：请加/减『秒数』或做差得到『间隔秒数』。"
            )
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    # 减：时间戳 - 秒数 -> 新时间戳；时间戳 - 时间戳 -> 相差秒数(float)
    def __sub__(self, other):
        if isinstance(other, (int, float, HumanTime, HumanTimestamp)):
            return HumanTime(float(self) - float(other))  # 返回间隔秒数
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float, HumanTime, HumanTimestamp)):
            return -self.__sub__(other)
        return NotImplemented

    # 乘/除：通常不常见，但保留为数值操作（结果仍为时间戳）
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self._wrap(float(self) * float(other))
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self._wrap(float(self) / float(other))
        if isinstance(other, HumanTimestamp):
            # 比值无明确语义，但保持数值行为，返回 float
            return float(self) / float(other)
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return self._wrap(float(self) // float(other))
        if isinstance(other, HumanTimestamp):
            return float(self) // float(other)
        return NotImplemented

    # ---------- 便捷方法 ----------
    @classmethod
    def now(cls, tz=None) -> HumanTimestamp:
        """
        返回当前时间的 HumanTimestamp 实例。

        :param tz: 时区，默认使用 DEFAULT_TZ。
        :return: 当前时间的 HumanTimestamp。
        """
        tz = tz or cls.DEFAULT_TZ
        return cls(datetime.now(tz), tz=tz)
