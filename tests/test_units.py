import pytest, logging
from zoneinfo import ZoneInfo

from celestialvault.instances.inst_units import HumanBytes, HumanTime, HumanTimestamp


def test_human_types():
    print("=== 🧮 HumanBytes 测试 ===")
    b1 = HumanBytes(123456789)
    b2 = HumanBytes("1GB 512MB")
    print("b1 =", b1)
    print("b2 =", b2)
    print("b1 + b2 =", b1 + b2)
    print("b1 * 2 =", b1 * 2)
    print("repr(b1) =", repr(b1))
    print()

    print("=== ⏱ HumanTime 测试 ===")
    t1 = HumanTime(5400.0)
    t2 = HumanTime("2h 15m 30s")
    print("t1 =", t1)
    print("t2 =", t2)
    print("t1 + t2 =", t1 + t2)
    print("t1 * 3 =", t1 * 3)
    print("repr(t2) =", repr(t2))
    print("负时长示例 =", HumanTime(-3700))
    print()

    print("=== 🕓 HumanTimestamp 测试 ===")
    ts1 = HumanTimestamp(1742978962.1039817)
    ts2 = HumanTimestamp.now()
    print("ts1 =", ts1)
    print("ts2 (now) =", ts2)
    print("ts2 - ts1 =", ts2 - ts1)  # 应返回 HumanTime
    print("ts1 + 60 =", ts1 + 60)
    print("repr(ts1) =", repr(ts1))
    print("ISO 格式:", ts1.to_iso())
    print("切换到 UTC:", ts1.with_tz(ZoneInfo("UTC")))
    print()

    print("✅ 所有测试执行完毕。")
