# `celestialvault.constants.style_parameters`

> 📅 最后更新日期: 2026/04/22

## 源文件
- `src/celestialvault/constants/style_parameters.py`

## 模块说明
定义图像生成的色彩风格参数和图片模式参数。色彩风格基于 HSV 色彩空间，每种风格通过 hue（色调）、saturation（饱和度）、value（明度）的范围来定义配色方案。模块顶部的文档字符串详细描述了色调（Hue）从 0 到 1 的完整色环变化：

- 红色 (Red): hue 0 ~ 0.05 (0 ~ 18 度)
- 橙色 (Orange): hue 0.05 ~ 0.1 (18 ~ 36 度)
- 黄色 (Yellow): hue 0.1 ~ 0.17 (36 ~ 61 度)
- 黄绿色 (Yellow-Green): hue 0.17 ~ 0.25 (61 ~ 90 度)
- 绿色 (Green): hue 0.25 ~ 0.42 (90 ~ 150 度)
- 青绿色 (Cyan): hue 0.42 ~ 0.5 (150 ~ 180 度)
- 蓝色 (Blue): hue 0.5 ~ 0.67 (180 ~ 240 度)
- 紫色 (Purple): hue 0.67 ~ 0.83 (240 ~ 300 度)
- 粉红 (Pink): hue 0.83 ~ 0.95 (300 ~ 342 度)
- 红色 (Red): hue 0.95 ~ 1 (342 ~ 360 度)

## 导入依赖
- 无

## 模块常量

### `style_params`
- **类型**: `dict[str, list[dict]]`
- **值**: 风格名称到 HSV 参数列表的映射，共 20 种风格
- **说明**: 每个风格包含一个或多个色域字典，字典键包括：
  - `hue_range`: `tuple[float, float]` -- 色调范围 (0-1)
  - `saturation_range`: `tuple[float, float]` -- 饱和度范围 (0-1)
  - `value_range`: `tuple[float, float]` -- 明度范围 (0-1)
  - `weight`: `int`（可选）-- 该色域的权重，用于多色域风格中控制颜色比例

#### 风格列表

| 风格名 | 中文名 | 色域数 | 描述 |
|--------|--------|--------|------|
| `morandi` | 莫兰迪 | 1 | 柔和、低饱和度的颜色 |
| `hawaiian` | 夏威夷 | 1 | 明亮热情的橙黄绿色调 |
| `deepsea` | 深海蓝调 | 1 | 深蓝色和绿色调，低亮度 |
| `twilight` | 暮光森林 | 1 | 深绿色和紫色调，神秘感 |
| `sunrise` | 日出暖阳 | 1 | 柔和的粉色、橙色和淡黄色 |
| `cyberpunk` | 工业未来 | 1 | 霓虹灯色调，高饱和度高亮度 |
| `autumn` | 秋天的怀旧 | 1 | 橙色、棕色和金色 |
| `aurora` | 极光幻影 | 1 | 绿色、蓝色和紫色，梦幻色彩 |
| `desert_twilight` | 沙漠暮光 | 2 | 沙色地面(权重4) + 浅紫色天空(权重1) |
| `coral_reef` | 珊瑚礁 | 2 | 橙粉珊瑚色(权重1) + 浅蓝海水(权重1) |
| `midnight_sky` | 午夜星空 | 2 | 深蓝低亮度 + 高亮度星光 |
| `candyland` | 糖果世界 | 2 | 粉紫色(权重3) + 黄绿色(权重2) |
| `volcanic_lava` | 火山熔岩 | 2 | 深红低亮(权重3) + 高亮熔岩光芒(权重1) |
| `frozen_wonderland` | 冰雪世界 | 1 | 淡蓝色、低饱和度、高亮度 |
| `tropical_rainforest` | 热带雨林 | 1 | 绿色到黄绿色，中高饱和度 |
| `sacred_flame` | 圣火 | 3 | 红橙(权重4) + 黄色(权重2) + 绿蓝光晕(权重1) |
| `wave_sky` | 澜与天 | 1 | 蓝色系，专为《林中花》定制 |

### `image_mode_params`
- **类型**: `dict[str, dict]`
- **值**: 图片模式名称到参数字典的映射，共 3 种模式
- **说明**: 每个模式字典包含以下键：
  - `channels`: `int` -- 通道数
  - `mode_name`: `str` -- Pillow 模式名称
  - `description`: `str` -- 模式描述

| 模式键名 | 通道数 | Pillow 模式 | 描述 |
|----------|--------|-------------|------|
| `grey` | 1 | `"L"` | 8-bit pixels, black and white |
| `rgb` | 3 | `"RGB"` | 3x8-bit pixels, true color |
| `rgba` | 4 | `"RGBA"` | 4x8-bit pixels, true color with transparency mask |

## 用法示例

```python
from celestialvault.constants.style_parameters import style_params, image_mode_params

# 获取莫兰迪风格参数
morandi = style_params["morandi"][0]
print(morandi["hue_range"])        # (0, 1)
print(morandi["saturation_range"]) # (0.1, 0.3)

# 获取多色域风格
for zone in style_params["sacred_flame"]:
    print(zone["hue_range"], zone.get("weight", 1))

# 列出所有可用风格名称
print(list(style_params.keys()))

# 获取图片模式参数
rgb_params = image_mode_params["rgb"]
print(rgb_params["mode_name"])  # "RGB"
print(rgb_params["channels"])   # 3
```

## 关联
- `style_params` 可用于图像生成工具中的随机配色方案选择
- `image_mode_params` 可用于图像处理模块中确定 Pillow 图片模式和通道数
- 与 `celestialvault.constants.image_format` 中的格式映射配合使用

## 顶层函数
- 无

## 类
- 无
