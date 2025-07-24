import pytest
from celestialvault.instances.inst_symmetric import SymmetricMap


def test_basic_insert_and_lookup():
    sm = SymmetricMap()
    sm["foo"] = "bar"
    assert sm["foo"] == "bar"
    assert sm["bar"] == "foo"
    assert "foo" in sm
    assert "bar" in sm

def test_conflict_raises():
    sm = SymmetricMap()
    sm["a"] = "b"
    try:
        sm["b"] = "c"
        assert False  # 应该不走到这
    except ValueError:
        assert True