# `celestialvault.constants.pi_digit`

> 📅 最后更新日期: 2026/04/22

## 源文件
- `src/celestialvault/constants/pi_digit.py`

## 模块说明
存储圆周率 Pi 的高精度字符串表示，包含 100 万位小数。

## 导入依赖
- 无

## 模块常量

### `PI_STR_1E6`
- **类型**: `str`
- **值**: 圆周率 Pi 的字符串表示，以 `"3."` 开头，包含 1,000,000 位小数
- **说明**: 可用于高精度数学计算、Pi 相关算法验证、数字艺术生成等场景

## 用法示例

```python
from celestialvault.constants.pi_digit import PI_STR_1E6

# 获取前 10 位小数
print(PI_STR_1E6[:12])  # "3.1415926535"

# 获取总长度（含 "3." 前缀）
print(len(PI_STR_1E6))  # 1000002

# 统计某个数字出现的次数
print(PI_STR_1E6.count("0"))
```

## 关联
- 可用于数学计算工具或数字艺术生成模块中作为 Pi 值的数据源

## 顶层函数
- 无

## 类
- 无
