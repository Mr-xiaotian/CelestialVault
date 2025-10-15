import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from celestialvault.tools.ImageProcessing import (
    expand_image,
    simulate_random_damage,
    restore_expanded_image,
    generate_palette, 
    palette_to_image
)


def evaluate_restore_effectiveness(
    image: Image.Image,
    n: int = 20,
    damage_ratio: float = 0.1,
    show: bool = True,
) -> dict:
    """
    测试 restore_expanded_image 的修复效果。

    流程：
    1. expand_image 放大图像
    2. simulate_random_damage 随机破坏
    3. restore_expanded_image 尝试恢复
    4. 与原图对比输出修复效果指标

    :param image: 原始图像
    :param n: 放大倍数
    :param damage_ratio: 损坏比例 (0~1)
    :param show: 是否显示可视化图像
    :return: 包含准确率和误差的 dict
    """
    # 1️⃣ 放大
    expanded = expand_image(image, n)

    # 2️⃣ 破坏
    damaged = simulate_random_damage(expanded, damage_ratio)

    # 3️⃣ 恢复
    restored = restore_expanded_image(damaged, n)

    # 4️⃣ 转为numpy比较
    arr_original = np.array(image.convert("RGB"))
    arr_restored = np.array(restored.convert("RGB"))

    # 对齐尺寸（防止某些模式不同导致尺寸略差）
    h, w = min(arr_original.shape[0], arr_restored.shape[0]), min(arr_original.shape[1], arr_restored.shape[1])
    arr_original, arr_restored = arr_original[:h, :w], arr_restored[:h, :w]

    # === 计算像素准确率 ===
    same_pixels = np.all(arr_original == arr_restored, axis=-1)
    accuracy = np.sum(same_pixels) / same_pixels.size

    # === 计算平均绝对误差 ===
    mae = np.mean(np.abs(arr_original.astype(np.int16) - arr_restored.astype(np.int16)))

    # === 可视化结果 ===
    if show:
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        axes[0].imshow(image)
        axes[0].set_title("Original")
        axes[1].imshow(damaged)
        axes[1].set_title(f"Damaged ({damage_ratio*100:.1f}%)")
        axes[2].imshow(restored)
        axes[2].set_title(f"Restored\nAcc={accuracy*100:.2f}%, MAE={mae:.2f}")
        for ax in axes:
            ax.axis("off")
        plt.tight_layout()
        plt.show()

    return {
        "accuracy": accuracy,
        "mae": mae,
        "damage_ratio": damage_ratio,
        "n": n,
    }

def evaluate_restore_curve(
    image: Image.Image,
    n: int = 20,
    damage_ratios: list[float] = [0.01, 0.05, 0.1, 0.2],
    show: bool = True,
) -> dict:
    """
    批量评估 restore_expanded_image 的修复效果，并将所有结果输出到一张图中。

    :param image: 原始图像
    :param n: 放大倍数
    :param damage_ratios: 要测试的损坏比例列表
    :param show: 是否显示图像
    :return: {'ratios': [...], 'accuracy': [...], 'mae': [...], 'restored_images': [...]}
    """
    results = {"ratios": [], "accuracy": [], "mae": [], "restored_images": []}

    arr_original = np.array(image.convert("RGB"))

    for damage_ratio in damage_ratios:
        expanded = expand_image(image, n)
        damaged = simulate_random_damage(expanded, damage_ratio)
        restored = restore_expanded_image(damaged, n)

        arr_restored = np.array(restored.convert("RGB"))
        h, w = min(arr_original.shape[0], arr_restored.shape[0]), min(arr_original.shape[1], arr_restored.shape[1])
        arr_o, arr_r = arr_original[:h, :w], arr_restored[:h, :w]

        same_pixels = np.all(arr_o == arr_r, axis=-1)
        accuracy = np.sum(same_pixels) / same_pixels.size
        mae = np.mean(np.abs(arr_o.astype(np.int16) - arr_r.astype(np.int16)))

        results["ratios"].append(damage_ratio)
        results["accuracy"].append(accuracy)
        results["mae"].append(mae)
        results["restored_images"].append((damage_ratio, damaged, restored))

    # ===== 绘制总览图 =====
    if show:
        n_ratios = len(damage_ratios)
        fig = plt.figure(figsize=(4 * n_ratios, 8))

        # 上方修复曲线
        ax_curve = plt.subplot2grid((2, n_ratios), (0, 0), colspan=n_ratios)
        ax_curve.plot(results["ratios"], np.array(results["accuracy"]) * 100, 'o-', label="Accuracy (%)")
        ax_curve.plot(results["ratios"], results["mae"], 's--', color='orange', label="MAE")
        ax_curve.set_xlabel("Damage Ratio")
        ax_curve.set_ylabel("Accuracy (%) / MAE")
        ax_curve.set_title(f"Restore Effectiveness (n={n})")
        ax_curve.legend()
        ax_curve.grid(True, linestyle="--", alpha=0.4)

        # 下方展示图像
        for i, (damage_ratio, damaged, restored) in enumerate(results["restored_images"]):
            ax_dmg = plt.subplot2grid((2, n_ratios), (1, i))
            ax_dmg.imshow(np.hstack([
                np.array(damaged.resize(image.size, Image.NEAREST)),
                np.array(restored.resize(image.size, Image.NEAREST))
            ]))
            acc = results["accuracy"][i] * 100
            ax_dmg.set_title(f"Damage {damage_ratio*100:.1f}%\nAcc={acc:.2f}%")
            ax_dmg.axis("off")

        plt.tight_layout()
        plt.show()

    return results


if __name__ == "__main__":
    palette = generate_palette(64, "morandi", "spiral")
    palette_img = palette_to_image(palette, 4)

    # === 评估 ===
    result_0 = evaluate_restore_effectiveness(palette_img, 10, 0.3, True)
    result_1 = evaluate_restore_curve(
        palette_img,
        n=10,
        damage_ratios=np.arange(0.0, 1.1, 0.1),
        show=True
    )

    print(result_0)
    print(result_1)