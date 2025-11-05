import random
import string
import shutil
from pathlib import Path
from typing import List, Union

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont


# ==== 文件操作工具函数 ====
def make_image_tree(root_dir: str | Path, num_dirs: int = 3, images_per_dir: int = 5):
    """
    在指定路径下生成多个子文件夹，每个文件夹中包含若干张大小随机、颜色不同的测试图片。

    :param root_dir: 根目录路径，将在其下创建子文件夹和图片
    :param num_dirs: 子文件夹数量
    :param images_per_dir: 每个子文件夹中生成的图片数量
    """
    root_dir = Path(root_dir)
    root_dir.mkdir(parents=True, exist_ok=True)

    for dir_idx in range(1, num_dirs + 1):
        sub_dir = root_dir / f"dir_{dir_idx}"
        sub_dir.mkdir(exist_ok=True)

        for img_idx in range(1, images_per_dir + 1):
            width = random.randint(300, 800)
            height = random.randint(300, 1000)
            color = tuple(random.randint(0, 255) for _ in range(3))

            img = Image.new("RGB", (width, height), color=color)
            draw = ImageDraw.Draw(img)

            text = f"{sub_dir.name}_{img_idx}\n{width}x{height}"
            try:
                font = ImageFont.truetype("arial.ttf", size=24)
            except:
                font = ImageFont.load_default()
            draw.text((10, 10), text, fill="white", font=font)

            img.save(sub_dir / f"img_{img_idx:02d}.jpg")

    print(f"✅ 成功生成 {num_dirs} 个子文件夹，每个包含 {images_per_dir} 张测试图片。")


def make_multisize_pdf(file_path: str | Path):
    """
    创建一个包含不同尺寸页面的示例 PDF 文件。

    :param file_path: 输出 PDF 文件的路径
    """
    # 创建新的 PDF 文档
    doc = fitz.open()

    # 页面 1 - A5 尺寸 (420x595)
    page = doc.new_page(width=420, height=595)
    page.insert_text((72, 100), "页面 1：A5 尺寸 (420x595)", fontsize=14)
    page.insert_text(
        (72, 130), "这是一个示例 PDF，页面尺寸较小，用于测试页面宽度调整功能。"
    )

    # 页面 2 - A4 尺寸 (595x842)
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 100), "页面 2：A4 尺寸 (595x842)", fontsize=14)
    page.insert_text((72, 130), "该页面的宽度较上一页更大，适用于文本内容较多的场景。")

    # 页面 3 - A3 尺寸 (842x1191)
    page = doc.new_page(width=842, height=1191)
    page.insert_text((72, 100), "页面 3：A3 尺寸 (842x1191)", fontsize=14)
    page.insert_text(
        (72, 130), "这是一个超宽页面，适用于需要展示更大图片或表格的场景。"
    )

    # 保存 PDF 文件
    doc.save(str(file_path))

    print(f"✅ 成功创建示例 PDF 文件：{file_path}")


def make_dirpair_fixture(base_path: str | Path):
    """
    在 base_path 下生成 dirA 和 dirB 两个文件夹，用于测试文件夹对比功能。
    覆盖四种情况：
    1. 名称、大小、内容均不同；
    2. 名称相同但大小、内容不同；
    3. 名称和大小相同但内容不同；
    4. 名称、大小、内容完全相同。

    :param base_path: 基础路径
    """
    base = Path(base_path)
    dirA = base / "dirA"
    dirB = base / "dirB"

    # 清理旧目录
    for d in (dirA, dirB):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    # ---------- ① 名称、大小、内容均不同 ----------
    fileA1 = dirA / "only_in_A.txt"
    fileB1 = dirB / "only_in_B.txt"
    fileA1.write_text("AAA" * 10)  # 长度 30
    fileB1.write_text("BBB" * 20)  # 长度 60

    (dirA / "diff_name_A").mkdir()
    (dirB / "diff_name_B").mkdir()
    (dirA / "diff_name_A" / "dataA.txt").write_text("This is A's data.")
    (dirB / "diff_name_B" / "dataB.txt").write_text("This is B's data.")

    # ---------- ② 名称相同但大小、内容不同 ----------
    fileA2 = dirA / "same_name_diff_size_content.txt"
    fileB2 = dirB / "same_name_diff_size_content.txt"
    fileA2.write_text("short text")  # 长度短
    fileB2.write_text("a bit longer text")  # 长度不同且内容不同

    subA2 = dirA / "same_name_diff_size_folder"
    subB2 = dirB / "same_name_diff_size_folder"
    subA2.mkdir()
    subB2.mkdir()
    (subA2 / "data.txt").write_text("A" * 10)
    (subB2 / "data.txt").write_text("B" * 20)

    # ---------- ③ 名称和大小相同但内容不同 ----------
    fileA3 = dirA / "same_name_size_diff_content.txt"
    fileB3 = dirB / "same_name_size_diff_content.txt"
    textA3 = "ABCDEFGH"  # 长度 8
    textB3 = "12345678"  # 同样长度 8，但内容不同
    fileA3.write_text(textA3)
    fileB3.write_text(textB3)

    subA3 = dirA / "same_name_size_diff_content_folder"
    subB3 = dirB / "same_name_size_diff_content_folder"
    subA3.mkdir()
    subB3.mkdir()
    (subA3 / "data.txt").write_text("abcdefghij")  # 长度 10
    (subB3 / "data.txt").write_text("ABCDEFGHIJ")  # 同长度但不同内容

    # ---------- ④ 名称、大小、内容完全相同 ----------
    fileA4 = dirA / "same_all.txt"
    fileA4.write_text("identical content")
    fileB4 = dirB / "same_all.txt"
    shutil.copy2(fileA4, fileB4)

    subA4 = dirA / "same_all_folder"
    subB4 = dirB / "same_all_folder"
    subA4.mkdir()
    (subA4 / "identical.txt").write_text("completely identical")
    shutil.copytree(subA4, subB4, dirs_exist_ok=True, copy_function=shutil.copy2)

    print(f"✅ 测试目录已生成:\n{dirA}\n{dirB}")
    return dirA, dirB


# ==== 测试数据生成函数 ====
def random_values(length: int, data_types: Union[str, List[str]] = None) -> List:
    """
    生成测试数据

    :param length: 数据数量
    :param data_types: 数据类型，可以是字符串（'str', 'int', 'float', 'bool', 'none', 'list', 'dict', 'bytes', 'choice'）
                       或列表（支持多选）。如果为 None，则默认全选所有类型。
    :return: 随机数据列表
    """
    all_types = [
        "str",
        "int",
        "float",
        "bool",
        "none",
        "list",
        "dict",
        "bytes",
        "choice",
    ]

    # 统一成列表形式
    if data_types is None:
        data_types = all_types
    elif isinstance(data_types, str):
        data_types = [data_types]
    else:
        # 过滤无效类型
        data_types = [t for t in data_types if t in all_types]
        if not data_types:
            raise ValueError(f"不支持的数据类型: {data_types}")

    def random_item(dtype: str):
        if dtype == "str":
            return "".join(
                random.choices(string.ascii_lowercase, k=random.randint(5, 10))
            )
        elif dtype == "int":
            return random.randint(-1000, 1000)
        elif dtype == "float":
            return round(random.uniform(-100, 100), 2)
        elif dtype == "bool":
            return random.choice([True, False])
        elif dtype == "none":
            return None
        elif dtype == "list":
            return [
                random_item(random.choice(data_types))
                for _ in range(random.randint(2, 5))
            ]
        elif dtype == "dict":
            return {
                f"k{i}": random_item(random.choice(data_types))
                for i in range(random.randint(1, 3))
            }
        elif dtype == "bytes":
            return bytes(random.getrandbits(8) for _ in range(random.randint(4, 8)))
        elif dtype == "choice":
            return random.choice(["apple", "banana", "cherry", "dog", "cat"])
        else:
            raise ValueError(f"不支持的数据类型: {dtype}")

    return [random_item(random.choice(data_types)) for _ in range(length)]


def rand_strict_increasing_ints(
    length: int, start: int = 0, max_step: int = 10
) -> list[int]:
    """
    生成一个随机递增整数序列

    :param length: 序列长度
    :param start: 起始值
    :param max_step: 每次递增的最大步长（至少 1）
    """
    seq = [start]
    for _ in range(length - 1):
        step = random.randint(1, max_step)  # 随机步长 ≥1 保证递增
        seq.append(seq[-1] + step)
    return seq


def rand_int_matrix(size, min_val=1, max_val=9):
    """
    生成一个方形二维数组（矩阵），元素为随机正整数。

    :param size: 矩阵大小（行数 = 列数）
    :param min_val: 元素最小值
    :param max_val: 元素最大值
    :return: 二维数组
    """
    matrix = [
        [random.randint(min_val, max_val) for _ in range(size)] for _ in range(size)
    ]
    return matrix


def fixed_length_series(n: int, digits: str = "0123456789") -> str:
    """
    生成一个“长度数”序列。

    :param n: 目标长度（1 <= n < 100），输出字符串的总长度。
    :param digits: 用来填充的字符序列，如 "0123456789" 或 "零一二三四五六七八九"。
                   默认值为 "0123456789"。
    :return: 一个长度恰好为 n 的字符串。
    """
    if not (1 <= n < 100):
        raise ValueError("n 必须在 1 到 99 之间")

    res = []
    need = n
    first_block = digits[1:]  # 去掉首字符，从第二个字符开始
    take = min(need, len(first_block))
    res.append(first_block[:take])
    need -= take

    # 后续块
    t = 1
    tail = digits[1:]
    while need > 0:
        # 当前块前缀为 digits[t]，若超出范围则循环使用
        prefix = digits[t % len(digits)]
        block = prefix + tail
        take = min(need, len(block))
        res.append(block[:take])
        need -= take
        t += 1

    return "".join(res)


def gapped_range_tuples(length: int, tuple_size: int):
    """
    生成指定数量和元组长度的递增数列元组列表

    :param length: 元组数量
    :param tuple_size: 每个元组的长度
    """
    result = []
    current = 0
    for _ in range(length):
        tup = tuple(rand_strict_increasing_ints(tuple_size, current))
        result.append(tup)
        current += tuple_size + 1  # 每组间隔 1
    return result
