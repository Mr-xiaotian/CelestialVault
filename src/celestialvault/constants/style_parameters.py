'''
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
'''

# 定义风格参数字典
style_params = {
    # 'grey': {
    #     'hue_range': (0, 0),
    #     'saturation_range': (0, 0),
    #     'value_range': (0, 1)
    # },
    'morandi': {
        # 莫兰迪风格，使用柔和、低饱和度的颜色
        'hue_range': (0, 1),  # 随机色调
        'saturation_range': (0.1, 0.3),  # 低饱和度
        'value_range': (0.7, 0.9)  # 较高亮度
    },
    'hawaiian': {
        # 夏威夷风格，使用明亮、热情的颜色，比如橙色、黄色和绿色
        'hue_range': (0.1, 0.6),  # 从橙色到绿色的色调
        'saturation_range': (0.7, 1.0),  # 高饱和度
        'value_range': (0.8, 1.0)  # 高亮度
    },
    'deepsea': {
        # 深海蓝调，使用深蓝色和绿色调，营造深海的感觉
        'hue_range': (0.5, 0.7),  # 蓝色到青色
        'saturation_range': (0.4, 0.7),  # 中等饱和度
        'value_range': (0.3, 0.5)  # 低亮度
    },
    'twilight': {
        # 暮光森林 (Twilight Forest)
        # 这种风格受森林在日落时分的微光启发, 使用深绿色和紫色调，营造神秘感
        'hue_range': (0.3, 0.8),  # 从深绿色到紫色
        'saturation_range': (0.3, 0.6),  # 低到中等饱和度
        'value_range': (0.2, 0.4)  # 较低亮度，模拟暮光的阴暗感
    },
    'sunrise': {
        # 日出暖阳 (Sunrise Glow)
        # 模拟日出时分的柔和色调, 柔和的粉色、橙色和淡黄色
        'hue_range': (0.0, 0.2),  # 从粉色到橙色
        'saturation_range': (0.5, 0.7),  # 中等饱和度
        'value_range': (0.7, 0.9)  # 较高亮度，表现温暖感
    },
    'cyberpunk': {
        # 工业未来 (Cyberpunk Neon)
        # 以现代城市的夜景为主题, 赛博朋克文化的霓虹灯色调
        'hue_range': (0.7, 0.9),  # 从紫色到蓝绿色
        'saturation_range': (0.8, 1.0),  # 非常高的饱和度，强烈对比
        'value_range': (0.7, 1.0)  # 高亮度，表现明亮醒目的霓虹灯光
    },
    'autumn': {
        # 秋天的怀旧 (Autumn Nostalgia)
        # 捕捉秋天的温暖色调, 以橙色、棕色和金色为主，带有一种怀旧的气息
        'hue_range': (0.05, 0.15),  # 从橙色到棕色
        'saturation_range': (0.4, 0.7),  # 低到中等饱和度
        'value_range': (0.4, 0.6)  # 较低到中等亮度，表现秋天的温暖
    },
    'aurora': {
        # 极光幻影 (Aurora Borealis)
        # 灵感来源于极光这种自然现象。极光常见于北极和南极地区的夜空中，
        # 以绚丽的绿色、蓝色和紫色为主，带有一种梦幻般的色彩和流动感。
        # 这些颜色给人一种神秘且超现实的感觉，适用于表现自然奇观和神秘氛围的设计。
        'hue_range': (0.4, 0.8),  # 从青绿色到紫色的色调，模拟极光的主要颜色
        'saturation_range': (0.5, 0.9),  # 中到高饱和度，增强色彩的明亮度
        'value_range': (0.6, 1.0)  # 较高亮度，使颜色显得更加流光溢彩
    },
    'desert_twilight': {
        # 沙漠暮光 (Desert Twilight)
        # 这一风格捕捉了沙漠黄昏时的宁静和温暖。黄昏的沙漠散发出独特的
        # 橙色和棕色调，天空则可能呈现出淡紫色。这个组合适合用于表现
        # 自然、宁静以及稍纵即逝的美景。
        'hue_range': (0.08, 0.15, 0.6, 0.75),  # 沙色到浅紫色，结合沙漠地面与黄昏的天空色调
        'saturation_range': (0.4, 0.7),  # 中等饱和度，避免过于鲜艳，使其保持柔和
        'value_range': (0.3, 0.5)  # 较低亮度，反映出黄昏时的光线衰减
    },
    'coral_reef': {
        # 珊瑚礁 (Coral Reef)
        # 珊瑚礁以其鲜艳的色彩和丰富的生物多样性著称。这种调色板风格
        # 捕捉了珊瑚礁的生命力和活力，颜色明亮而生动，适合表现自然生机
        # 和热带水下世界的多样性。
        'hue_range': (0.05, 0.15, 0.5, 0.6),  # 橙色到粉色，再到浅蓝色，模仿珊瑚和清澈海水的色调
        'saturation_range': (0.7, 1.0),  # 高饱和度，突显珊瑚礁的鲜艳和生命力
        'value_range': (0.7, 1.0)  # 高亮度，反映出阳光照射下的明亮色彩
    },
    'midnight_sky': {
        # 午夜星空 (Midnight Sky)
        # 这一风格着重表现夜晚的深邃和静谧。深蓝色和蓝紫色的调子，
        # 加上偶尔点缀的高亮度颜色，模仿夜空中的星光。这种风格适合用于
        # 创造宁静、冥想或神秘的氛围。
        'hue_range': (0.6, 0.75),  # 深蓝色到蓝紫色，模拟午夜时分的天空
        'saturation_range': (0.2, 0.5),  # 低到中等饱和度，反映夜空的柔和与暗淡
        'value_range': (0.1, 0.3, 0.8, 1.0)  # 低亮度为主，偶尔点缀高亮度模拟星星的闪烁
    },
    'candyland': {
        # 糖果世界 (Candyland)
        # 这个风格充满童趣和欢乐，以鲜艳的粉色、紫色、黄色和绿色为主。
        # 这些颜色常见于糖果和甜点中，能够唤起甜美、开心的情绪，适合
        # 用于儿童相关的设计或任何希望传递愉悦氛围的场景。
        'hue_range': (0.85, 1.0, 0.1, 0.2),  # 粉色到紫色，黄色到绿色，营造缤纷的糖果色
        'saturation_range': (0.8, 1.0),  # 非常高的饱和度，确保色彩的鲜艳和吸引力
        'value_range': (0.8, 1.0)  # 高亮度，使颜色显得更加明亮愉悦
    },
    'volcanic_lava': {
        # 火山熔岩 (Volcanic Lava)
        # 这一风格捕捉了火山喷发时的炽热和剧烈的能量。深红色和橙色
        # 象征着熔岩的流动，而黑色则代表火山的岩石。这种风格适合用
        # 于表现极端、力量或激烈的主题。
        'hue_range': (0.0, 0.05),  # 深红色到橙色，模仿炽热的熔岩流
        'saturation_range': (0.8, 1.0),  # 高饱和度，突显熔岩的强烈能量
        'value_range': (0.2, 0.4, 0.7, 0.9)  # 低亮度为主，但有时也会有高亮度模拟熔岩的光芒
    },
    'frozen_wonderland': {
        # 冰雪世界 (Frozen Wonderland)
        # 这一风格以冰雪覆盖的冬季景象为灵感，使用淡蓝色、浅灰色
        # 和白色来表现寒冷和纯净。适合用于冬季主题、冰雪场景或任何
        # 需要表现清冷、宁静氛围的设计。
        'hue_range': (0.5, 0.6),  # 从浅蓝色到淡灰色，模仿冰雪反射的光线
        'saturation_range': (0.1, 0.3),  # 低饱和度，表现冰雪的柔和色调
        'value_range': (0.8, 1.0)  # 高亮度，表现冰雪世界的纯净和明亮
    },
    'tropical_rainforest': {
        # 热带雨林 (Tropical Rainforest)
        # 灵感来自热带雨林的繁茂植被和生机勃勃的生态系统。绿色和黄色
        # 的调子代表了茂密的树冠和明亮的阳光穿透雨林的瞬间。这个组合
        # 适合用于表现自然活力和生物多样性的设计。
        'hue_range': (0.25, 0.35),  # 绿色到黄绿色，模拟树叶和阳光的色调
        'saturation_range': (0.6, 0.9),  # 中到高饱和度，展现雨林的活力
        'value_range': (0.5, 0.7)  # 中等亮度，表现出雨林的茂密与生机
    },
    'sacred_flame': {
        # 圣火 (Sacred Flame)
        # 这一风格灵感来源于神圣的火焰，象征着强大的生命力和不朽的能量。
        # 明亮的蓝色、黄色和绿色调结合在一起，表现出燃烧的光芒和活力。
        # 这种色彩组合非常适合用于需要表现力量、激情和光明的设计场景。
        'hue_range': (0,0.05, 0.16, 0.18, 0.47, 0.52),  # 主要集中在黄色及其附近的色调，适量加入绿色和少量蓝色
        'saturation_range': (0.8, 1.0),  # 高饱和度，表现出色彩的强烈和鲜明
        'value_range': (0.8, 1.0)  # 高亮度，体现出火焰般的光辉
    }
}

image_mode_params = {
    'grey': {  # 灰度模式
        'channels': 1,
        'mode_name': "L",
        'description': "8-bit pixels, black and white"
    },
    'rgb': {  # 彩色模式
        'channels': 3,
        'mode_name': "RGB",
        'description': "3x8-bit pixels, true color"
    },
    'rgba': {  # 彩色模式带透明通道
        'channels': 4,
        'mode_name': "RGBA",
        'description': "4x8-bit pixels, true color with transparency mask"
    },
    'palette': {  # 调色板模式
        'channels': 1,  # 实际上每个像素存储的是调色板索引
        'mode_name': "P",
        'description': "8-bit pixels, mapped to any other mode using a color palette"
    },
    'cmyk': {  # 印刷用色彩模型
        'channels': 4,
        'mode_name': "CMYK",
        'description': "4x8-bit pixels, color separation"
    },
    # 'ycbcr': {  # 颜色视频格式
    #     'channels': 3,
    #     'mode_name': "YCbCr",
    #     'description': "3x8-bit pixels, color video format"
    # },
    'lab': {  # Lab 色彩空间
        'channels': 3,
        'mode_name': "LAB",
        'description': "3x8-bit pixels, L*a*b color space"
    },
    'hsv': {  # 色调、饱和度、明度
        'channels': 3,
        'mode_name': "HSV",
        'description': "3x8-bit pixels, Hue, Saturation, Value color space"
    },
    # '1bit': {  # 单通道黑白图像
    #     'channels': 1,
    #     'mode_name': "1",
    #     'description': "1-bit pixels, black and white"
    # },
    # '32bit_integer': {  # 32位有符号整数像素
    #     'channels': 1,
    #     'mode_name': "I",
    #     'description': "32-bit signed integer pixels"
    # },
    # '32bit_float': {  # 32位浮点数像素
    #     'channels': 1,
    #     'mode_name': "F",
    #     'description': "32-bit floating point pixels"
    # }
}