import pytest
from celestialvault.instances.inst_symmetric import SymmetricMap


def test_symmetric_map_basic():
    m = SymmetricMap()
    m['a'] = 'b'
    assert m['a'] == 'b' and m['b'] == 'a'
    assert 'a' in m and 'b' in m and len(m) == 1

    m['x'] = 'y'
    assert set(m.keys()) == {'a', 'x'}
    assert set(m.values()) == {'b', 'y'}
    assert set(m.items()) == {('a', 'b'), ('x', 'y')}

    # 幂等设置
    m['a'] = 'b'  # 不应改变内容
    assert len(m) == 2

    # 变更配对
    m['a'] = 'y'  # 会先解绑 a<->b 与 x<->y，再建立 a<->y
    assert 'b' not in m and 'x' not in m and len(m) == 1 and m['a'] == 'y'

