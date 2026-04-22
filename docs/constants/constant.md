# `celestialvault.constants.constant`

> 📅 最后更新日期: 2026/04/22

## 源文件
- `src/celestialvault/constants/constant.py`

## 模块说明
通用常量模块，包含 User-Agent 列表、HTTP 请求头示例、RGB 颜色常量、中国城市坐标数据以及康熙部首/CJK 部首映射字典。版本 1.01，作者：晓天。

## 导入依赖
- 无

## 模块常量

### `user_agent_list`
- **类型**: `list[str]`
- **值**: 包含 10 个常用浏览器 User-Agent 字符串（Chrome、Firefox 等）
- **说明**: 用于 HTTP 请求伪装，模拟不同浏览器访问

### `zh_headers_test`
- **类型**: `str`
- **值**: 多行字符串，包含完整的中文网站（知乎）HTTP 请求头示例
- **说明**: 包含 accept、cookie、x-api-version 等字段，用于测试或参考

### RGB 颜色常量
| 常量名 | 类型 | 值 |
|--------|------|------|
| `GRAY` | `tuple[int, int, int]` | `(100, 100, 100)` |
| `NAVYBLUE` | `tuple[int, int, int]` | `(60, 60, 100)` |
| `WHITE` | `tuple[int, int, int]` | `(240, 240, 240)` |
| `RED` | `tuple[int, int, int]` | `(255, 0, 0)` |
| `GREEN` | `tuple[int, int, int]` | `(0, 255, 0)` |
| `BLUE` | `tuple[int, int, int]` | `(0, 0, 255)` |
| `YELLOW` | `tuple[int, int, int]` | `(255, 255, 0)` |
| `ORANGE` | `tuple[int, int, int]` | `(255, 128, 0)` |
| `PURPLE` | `tuple[int, int, int]` | `(255, 0, 255)` |
| `CYAN` | `tuple[int, int, int]` | `(0, 255, 255)` |
| `BLACK` | `tuple[int, int, int]` | `(0, 0, 0)` |
| `DARKGREEN` | `tuple[int, int, int]` | `(0, 155, 0)` |
| `DARKGRAY` | `tuple[int, int, int]` | `(40, 40, 40)` |

### `COLOR_LIST`
- **类型**: `list[tuple[int, int, int]]`
- **值**: `[GRAY, NAVYBLUE, WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, BLACK]`
- **说明**: 常用颜色常量的列表集合（不含 DARKGREEN 和 DARKGRAY）

### `city_coordinate`
- **类型**: `dict[str, list[float]]`
- **值**: 约 350 个中国城市名称到坐标的映射，格式为 `"城市名": [纬度, 经度]`
- **说明**: 坐标顺序为 `[lat, lng]`

### `new_city_coordinate`
- **类型**: `dict[str, list[float]]`
- **值**: 与 `city_coordinate` 相同的城市集合，但坐标顺序为 `[经度, 纬度]`
- **说明**: 坐标顺序为 `[lng, lat]`，与 `city_coordinate` 互为转置

### `KangxiRadicalsDict`
- **类型**: `dict[str, str]`
- **值**: 康熙部首字符（U+2F00 - U+2FDF）到对应简体中文汉字的映射，共 226 个条目
- **说明**: 用于将康熙部首 Unicode 字符转换为对应的现代汉字

### `CJKRadicalsSupplementDict`
- **类型**: `dict[str, str]`
- **值**: CJK 部首补充字符（U+2E80 - U+2EFF）到对应简体中文汉字的映射，共 129 个条目
- **说明**: 用于将 CJK 部首补充区的 Unicode 字符转换为对应的现代汉字

## 用法示例

```python
from celestialvault.constants.constant import user_agent_list, RED, city_coordinate

# 随机选择一个 User-Agent
import random
headers = {"User-Agent": random.choice(user_agent_list)}

# 使用颜色常量
print(RED)  # (255, 0, 0)

# 查询城市坐标
print(city_coordinate["北京"])  # [39.9299857781, 116.395645038]
```

## 关联
- `user_agent_list` 可用于网络爬取模块中的请求伪装
- RGB 颜色常量和 `COLOR_LIST` 可用于图像处理、可视化等模块
- `city_coordinate` / `new_city_coordinate` 可用于地图可视化工具
- `KangxiRadicalsDict` / `CJKRadicalsSupplementDict` 可用于文本处理工具中的 Unicode 规范化

## 顶层函数
- 无

## 类
- 无
