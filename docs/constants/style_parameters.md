# constants/style_parameters.py

## 源文件
- `src/celestialvault/constants/style_parameters.py`

## 模块说明
色调 (Hue) 的范围和颜色变化

红色 (Red)：

范围：hue 在 0 到 0.05（或 0° 到 18°）之间。
颜色变化：从深红到亮红，随着 hue 增加，红色逐渐变亮，并开始接近橙色。
橙色 (Orange)：

范围：hue 在 0.05 到 0.1（或 18° 到 36°）之间。
颜色变化：从红橙到亮橙，颜色从红色过渡到橙色，再逐渐接近黄色。
黄色 (Yellow)：

范围：hue 在 0.1 到 0.17（或 36° 到 61°）之间。
颜色变化：从橙黄色到亮黄色，随着 hue 增加，橙色逐渐变为更纯的黄色。
黄绿色 (Yellow-Green)：

范围：hue 在 0.17 到 0.25（或 61° 到 90°）之间。
颜色变化：从亮黄色到青绿色，黄色逐渐转变为带有绿色调的黄绿色，最后接近纯绿色。
绿色 (Green)：

范围：hue 在 0.25 到 0.42（或 90° 到 150°）之间。
颜色变化：从黄绿色到纯绿色，再逐渐过渡到蓝绿色。
青绿色 (Cyan)：

范围：hue 在 0.42 到 0.5（或 150° 到 180°）之间。
颜色变化：从绿色过渡到青色，最终到达接近蓝色的青绿色。
蓝色 (Blue)：

范围：hue 在 0.5 到 0.67（或 180° 到 240°）之间。
颜色变化：从青绿色逐渐变为纯蓝色，然后向紫蓝色过渡。
紫色 (Purple)：

范围：hue 在 0.67 到 0.83（或 240° 到 300°）之间。
颜色变化：从蓝色过渡到紫色，紫色逐渐变为偏红的紫色。
粉红 (Pink)：

范围：hue 在 0.83 到 0.95（或 300° 到 342°）之间。
颜色变化：从紫色到粉红色，最后逐渐接近红色。
红色 (Red)：

范围：hue 在 0.95 到 1（或 342° 到 360°）之间。
颜色变化：从粉红色逐渐返回红色，形成一个完整的色环。

## 导入依赖
- 无

## 模块常量
### `style_params`
- 定义 17 种调色板风格的 HSV 参数字典。每种风格包含一个或多个色域，每个色域指定：
  - `hue_range` — 色调范围
  - `saturation_range` — 饱和度范围
  - `value_range` — 明度范围
  - `weight`（可选）— 该色域的采样权重
- 可用风格: morandi, hawaiian, deepsea, twilight, sunrise, cyberpunk, autumn, aurora, desert_twilight, coral_reef, midnight_sky, candyland, volcanic_lava, frozen_wonderland, tropical_rainforest, sacred_flame, wave_sky

### `image_mode_params`
- 图片模式参数字典，定义了不同图像模式的通道数和 PIL 模式名称：
  - `grey` — 1 通道, PIL 模式 `"L"`, 8-bit 灰度
  - `rgb` — 3 通道, PIL 模式 `"RGB"`, 真彩色
  - `rgba` — 4 通道, PIL 模式 `"RGBA"`, 真彩色带透明通道

## 顶层函数
- 无

## 类
- 无
