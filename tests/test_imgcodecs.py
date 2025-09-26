import pytest, logging
import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from PIL import Image

from celestialflow import TaskManager
from celestialvault.instances.inst_imgcodecs import BaseCodec, CODEC_REGISTRY


class TestDamageManager(TaskManager):
    codec: BaseCodec
    img: Image.Image
    text: str
    def get_args(self, task):
         w, h = task
         return self.codec, self.img, self.text, w, h
    
    def process_result_dict(self):
        return super().process_result_dict()


def _test_codecs_text():
    """
    测试所有注册的 codec 是否能正确进行 编码 -> 解码
    """
    sample_text = "Hello, 世界! 12345"

    for mode, codec in CODEC_REGISTRY.items():
        print(f"\n[TEST] Mode = {mode}")

        # 1. 编码
        img = codec.encode(sample_text)
        print(f"  Encoded image size: {img.size}, mode: {img.mode}")

        # 2. 解码
        decoded_text = codec.decode(img)

        # 3. 校验
        if decoded_text == sample_text:
            print("  ✅ Decode success, text matches")
        else:
            print("  ❌ Decode mismatch!")
            print("     Original:", repr(sample_text))
            print("     Decoded :", repr(decoded_text))

def _test_codecs_file():
    """
    测试所有注册的 codec 是否能正确进行 文件编码 -> 文件解码
    """
    sample_text_path = r"Q:\Project\test\text\test.txt"

    for mode, codec in CODEC_REGISTRY.items():
        print(f"\n[TEST] Mode = {mode}")

        # 1. 编码
        img = codec.encode_text_file(sample_text_path)
        print(f"  Encoded image size: {img.size}, mode: {img.mode}")

        # 2. 解码
        image_path = sample_text_path.replace('.txt', f'({codec.mode_name}).png')
        decoded_text = codec.decode_image_file(image_path)
        print(f"  Decoded text length: {len(decoded_text)}")


def simulate_damage(img: Image.Image, x0: int, y0: int, w: int, h: int) -> Image.Image:
    damaged = img.copy()
    pixels = damaged.load()
    for y in range(y0, min(y0 + h, img.height)):
        for x in range(x0, min(x0 + w, img.width)):
            pixels[x, y] = (0, 0, 0, 0)  # RGBA 清零
    return damaged

def is_damage_block(codec: BaseCodec, img, text: str, w: int, h: int) -> int:
    """
    在左上角损坏 w×h 区域，测试是否还能成功解码。
    :param codec: 编解码器
    :param img: 原始图像
    :param text: 原始文本
    :param w: 损坏宽度
    :param h: 损坏高度
    :return: 1=成功恢复, 0=失败
    """
    damaged_img = simulate_damage(img, 0, 0, w, h)
    try:
        decoded_text = codec.decode(damaged_img)
        return 1 if decoded_text == text else 0
    except Exception:
        return 0

def redundancy_heatmap(codec: BaseCodec, text: str):
    """
    对不同大小的损坏区域做测试，生成热力图。
    :param codec: 一个 codec 实例（如 rgba_redundancy）
    :param text: 要编码的文本
    """
    print(f"原始文本长度: {len(text)}")

    # 编码
    img = codec.encode(text)
    width, height = img.size
    print(f"编码后图像大小: {width}x{height}")

    # 结果矩阵
    result = np.zeros((height, width))

    test_damage_manager = TestDamageManager(is_damage_block, "thread", 5, enable_result_cache=True, show_progress=True)
    test_damage_manager.codec = codec
    test_damage_manager.img = img
    test_damage_manager.text = text

    test_damage_manager.start(product(range(1, width+1), range(1, height+1)))
    result_dict = test_damage_manager.process_result_dict()

    for (w, h), success in result_dict.items():
        result[h-1, w-1] = success
    
    # 设置字体为SimHei（黑体）
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决坐标轴负号显示问题
    plt.rcParams['axes.unicode_minus'] = False

    # 画热力图
    plt.figure(figsize=(8, 6))
    plt.imshow(result, origin="lower", cmap="RdYlGn", extent=[1, width, 1, height], aspect="auto")
    plt.colorbar(label="是否成功 (1=成功, 0=失败)")
    plt.xlabel("损坏区域宽度")
    plt.ylabel("损坏区域高度")
    plt.title("冗余模式鲁棒性热力图")
    plt.show()

if __name__ == "__main__":
    codec = CODEC_REGISTRY["rgba_redundancy"]
    codec.show_progress = False
    text = "Hello World! " * int(4e5)  # 足够长的测试文本(1e3, 4e5)

    redundancy_heatmap(codec, text)
