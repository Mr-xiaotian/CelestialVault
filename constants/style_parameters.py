# 定义风格参数字典
style_params = {
    'morandi': {
        # 莫兰迪风格，使用柔和、低饱和度的颜色
        'hue_range': (0, 1),  # 随机色调
        'saturation_range': (0.1, 0.3),  # 低饱和度
        'value_range': (0.7, 0.9)  # 较高亮度
    },
    'grey': {
        'hue_range': (0, 0),
        'saturation_range': (0, 0),
        'value_range': (0, 1)
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
        # 暮光森林，使用深绿色和紫色调，营造神秘感
        'hue_range': (0.3, 0.8),  # 从深绿色到紫色
        'saturation_range': (0.3, 0.6),  # 低到中等饱和度
        'value_range': (0.2, 0.4)  # 较低亮度，模拟暮光的阴暗感
    },
    'sunrise': {
        # 日出暖阳，柔和的粉色、橙色和淡黄色
        'hue_range': (0.0, 0.2),  # 从粉色到橙色
        'saturation_range': (0.5, 0.7),  # 中等饱和度
        'value_range': (0.7, 0.9)  # 较高亮度，表现温暖感
    },
    'cyberpunk': {
        # 工业未来风格，赛博朋克文化的霓虹灯色调
        'hue_range': (0.7, 0.9),  # 从紫色到蓝绿色
        'saturation_range': (0.8, 1.0),  # 非常高的饱和度，强烈对比
        'value_range': (0.7, 1.0)  # 高亮度，表现明亮醒目的霓虹灯光
    },
    'autumn': {
        # 秋天的怀旧，温暖的橙色、棕色和金色
        'hue_range': (0.05, 0.15),  # 从橙色到棕色
        'saturation_range': (0.4, 0.7),  # 低到中等饱和度
        'value_range': (0.4, 0.6)  # 较低到中等亮度，表现秋天的温暖
    }
}