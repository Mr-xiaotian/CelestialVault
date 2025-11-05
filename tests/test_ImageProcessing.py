import pytest, logging
from PIL import Image

from celestialvault.tools.ImageProcessing import (
    create_image_with_text_chunk,
    read_text_chunks,
)


def test_create_image_with_text_chunk():
    # 创建一张空白图
    img = Image.new("RGB", (100, 100), color="white")

    # 写入 metadata
    messages = {"Author": "Vault", "Comment": "Hello from CelestialVault!"}
    create_image_with_text_chunk(img, r"Q:\Project\test\test_meta.png", messages)

    # 读取 metadata
    meta = read_text_chunks(r"Q:\Project\test\test_meta.png")
    print(meta)
