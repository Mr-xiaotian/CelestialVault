import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from PIL import Image

from celestialflow import TaskManager
from celestialvault.instances.inst_imgcodecs import BaseCodec, CODEC_REGISTRY
from celestialvault.tools.ImageProcessing import (
    simulate_rectangle_damage,
    simulate_random_damage,
)


class RectangleDamageManager(TaskManager):
    codec: BaseCodec
    img: Image.Image
    text: str

    def get_args(self, task):
        w, h = task
        return self.codec, self.img, self.text, w, h

    def process_result_dict(self):
        return self.get_success_dict()


class RandomDamageManager(TaskManager):
    codec: BaseCodec
    img: Image.Image
    text: str

    def get_args(self, task):
        damage_ratio = task
        return self.codec, self.img, self.text, damage_ratio, 100

    def process_result_dict(self):
        return self.get_success_dict()


def success_rate_rectangle_damage_block(
    codec: BaseCodec, img: Image.Image, text: str, w: int, h: int
) -> int:
    """
    在左上角损坏 w×h 区域，测试是否还能成功解码。
    :param codec: 编解码器
    :param img: 原始图像
    :param text: 原始文本
    :param w: 损坏宽度
    :param h: 损坏高度
    :return: 1=成功恢复, 0=失败
    """
    damaged_img = simulate_rectangle_damage(img, 0, 0, w, h)
    try:
        decoded_text = codec.decode_text(damaged_img)
        return 1 if decoded_text == text else 0
    except Exception:
        return 0


def success_rate_random_damage(
    codec: BaseCodec, img: Image.Image, text: str, damage_ratio: float, trials: int = 10
) -> float:
    """
    随机损坏图像像素，重复多次测试成功率。

    :param codec: 编解码器
    :param img: 原始图像
    :param text: 原始文本
    :param damage_ratio: 损坏比例 (0~1)
    :param trials: 重复次数，默认 10
    :return: 成功率 (0~1 浮点数)
    """
    success_count = 0
    for _ in range(trials):
        damaged_img = simulate_random_damage(
            img, damage_ratio
        )  # 之前的 simulate_random_damage 改名
        try:
            decoded_text = codec.decode_text(damaged_img)
            if decoded_text == text:
                success_count += 1
        except Exception:
            continue
    return success_count / trials


def redundancy_heatmap(codec: BaseCodec, text: str):
    """
    对不同大小的损坏区域做测试，生成热力图。
    :param codec: 一个 codec 实例（如 rgba_redundancy）
    :param text: 要编码的文本
    """
    print(f"原始文本长度: {len(text)}")

    # 编码
    img = codec.encode_text(text)
    width, height = img.size
    print(f"编码后图像大小: {width}x{height}")

    # 结果矩阵
    result = np.zeros((height, width))

    rectangle_damage_manager = RectangleDamageManager(
        success_rate_rectangle_damage_block,
        "serial",
        enable_success_cache=True,
        show_progress=True,
    )
    rectangle_damage_manager.codec = codec
    rectangle_damage_manager.img = img
    rectangle_damage_manager.text = text

    random_damage_manager = RandomDamageManager(
        success_rate_random_damage,
        "process",
        5,
        enable_success_cache=True,
        show_progress=True,
    )
    random_damage_manager.codec = codec
    random_damage_manager.img = img
    random_damage_manager.text = text

    rectangle_damage_manager.start(product(range(1, width + 1), range(1, height + 1)))
    rectangle_damage_result_dict = rectangle_damage_manager.process_result_dict()

    ratios = np.arange(0, 1.01, 0.01)  # 从0到1，步长0.01
    random_damage_manager.start(ratios)
    random_damage_result_dict = random_damage_manager.process_result_dict()
    success_rates = [random_damage_result_dict[r] for r in ratios]

    for (w, h), success in rectangle_damage_result_dict.items():
        result[h - 1, w - 1] = success

    # 设置字体为SimHei（黑体）
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    # 解决坐标轴负号显示问题
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 左边：矩形损坏热力图
    im = axes[0].imshow(
        result,
        origin="lower",
        cmap="RdYlGn",
        extent=[1, width, 1, height],
        aspect="auto",
    )
    fig.colorbar(im, ax=axes[0], label="是否成功 (1=成功, 0=失败)")
    axes[0].set_xlabel("损坏区域宽度")
    axes[0].set_ylabel("损坏区域高度")
    axes[0].set_title(f"{codec.mode_name} 矩形损坏鲁棒性")

    # 右边：随机损坏曲线
    axes[1].plot(ratios, success_rates, marker="o", color="blue")
    axes[1].set_xlabel("损坏比例")
    axes[1].set_ylabel("成功率")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title(f"{codec.mode_name} 随机损坏鲁棒性")
    axes[1].grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.show()


# 递归绘制分段
def draw_segments_ratio(ax, segments, y=0, x_start=0, x_end=1):
    total_ratio = sum(r for _, r, _ in segments)
    cur_x = x_start
    for label, ratio, subseg in segments:
        width = (x_end - x_start) * (ratio / total_ratio)
        ax.add_patch(
            plt.Rectangle(
                (cur_x, y), width, 0.1, facecolor="#c8e6c9", edgecolor="black"
            )
        )
        ax.text(
            cur_x + width / 2, y + 0.05, label, ha="center", va="center", fontsize=9
        )
        if subseg:
            draw_segments_ratio(ax, subseg, y - 0.15, cur_x, cur_x + width)
        cur_x += width


def plot_segments_ratio():
    # 按比例绘制（pad_binary : rs冗余 = 70% : 30%）
    segments_ratio = [
        (
            "pad_binary ~70%",
            0.7,
            [
                ("原始长度头(4B)", 0.05, None),
                (
                    "compressed_binary",
                    0.75,
                    [
                        ("压缩长度头(4B)", 0.1, None),
                        (
                            "zlib压缩数据",
                            0.9,
                            [
                                (
                                    "crc_text",
                                    1.0,
                                    [("CRC32(4B)", 0.1, None), ("原始数据", 0.9, None)],
                                )
                            ],
                        ),
                    ],
                ),
                ("填充(0xEC,0x11...)", 0.2, None),
            ],
        ),
        ("RS冗余码(nsym) ~30%", 0.3, None),
    ]
    # 设置字体为SimHei（黑体）
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    # 解决坐标轴负号显示问题
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(60, 5))
    draw_segments_ratio(ax, segments_ratio, y=0, x_start=0, x_end=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.8, 0.3)
    ax.axis("off")
    # plt.show()

    # 保存图片
    plt.savefig(
        "img/rs_binary_segments_ratio.png", bbox_inches="tight", pad_inches=0.05
    )


if __name__ == "__main__":
    codec = CODEC_REGISTRY["morandi_rs"]  # morandi_rs rgba_redundancy
    codec.show_progress = False
    text = "Hello World! " * int(1e3)  # 足够长的测试文本(1e3, 4e5)

    redundancy_heatmap(codec, text)
    # plot_segments_ratio()
