import pytest, logging
from pathlib import Path
from celestialvault.instances.inst_imgcodecs import CODEC_REGISTRY


def test_codecs_text():
    """
    测试所有注册的 codec 是否能正确进行 编码 -> 解码（纯文本）
    """
    sample_text = "Hello, 世界! 12345 This is a test text with special chars: \n\t\r!@#$%^&*()_+-=[]{}|;:',.<>/?`~"
    exist_error = False

    for mode, codec in CODEC_REGISTRY.items():
        print(f"\n[TEST] Mode = {mode}")

        try:
            # 1. 编码
            img = codec.encode_text(sample_text)
            print(f"  Encoded image size: {img.size}, mode: {img.mode}")

            # 2. 解码
            decoded_text = codec.decode_text(img)

        except Exception as e:
            print(f"  ❌ Exception during encoding/decoding: {e}")
            exist_error = True
            continue

    assert not exist_error, "Some codecs failed during text encoding/decoding."


def test_codecs_bytes():
    """
    测试所有注册的 byte-codec 是否能正确进行 编码 -> 解码（纯 bytes）
    """
    sample_data = b"Hello\x00\xFFWorld\x10\x20Binary!\xAB\xCD"
    exist_error = False

    for mode, codec in CODEC_REGISTRY.items():
        print(f"\n[TEST] Mode = {mode}")

        try:
            # 1. 编码
            img = codec.encode_bytes(sample_data)
            print(f"  Encoded image size: {img.size}, mode: {img.mode}")

            # 2. 解码
            decoded_data = codec.decode_bytes(img)

        except Exception as e:
            print(f"  ❌ Exception during encoding/decoding: {e}")
            exist_error = True
            continue

    assert not exist_error, "Some codecs failed during bytes encoding/decoding."


def test_codecs_txt_file():
    """
    测试所有 codec 是否能正确进行 文本文件 -> 图像 -> 文本文件 的编解码
    """
    sample_text_path = r"Q:\Project\test\text\text_txt.txt"
    exist_error = False

    for mode, codec in CODEC_REGISTRY.items():
        print(f"\n[TEST] Mode = {mode}")

        try:
            # 1. 编码
            img = codec.encode_txt_file(sample_text_path, True)
            print(f"  Encoded image size: {img.size}, mode: {img.mode}")

            # 2. 解码
            image_path = sample_text_path.replace(".txt", f"({codec.mode_name})(txt).png")
            decoded_text = codec.decode_txt_image_file(image_path)
            print(f"  Decoded text length: {len(decoded_text)}")

        except Exception as e:
            print(f"  ❌ Exception during text-file encoding/decoding: {e}")
            exist_error = True
            continue

    assert not exist_error, "Some codecs failed during text-file encoding/decoding."


def test_codecs_binary_file():
    """
    测试所有 codec 是否能正确进行 二进制文件 -> 图像 -> 二进制文件 的编解码
    """
    sample_bin_path = r"Q:\Project\test\binary\test_pdf.pdf"
    exist_error = False

    for mode, codec in CODEC_REGISTRY.items():
        print(f"\n[TEST] Mode = {mode}")

        try:
            # 1. 编码
            img = codec.encode_binary_file(sample_bin_path, True)
            print(f"  Encoded image size: {img.size}, mode: {img.mode}")

            # 2. 解码
            # 解析输出图像名：<stem>(mode)(ext).png
            p = Path(sample_bin_path)
            image_name = f"{p.stem}({codec.mode_name})({p.suffix[1:]}).png"
            image_path = p.with_name(image_name)

            decoded_bytes = codec.decode_binary_image_file(image_path)
            print(f"  Decoded binary size: {len(decoded_bytes)}")

        except Exception as e:
            print(f"  ❌ Exception during binary-file encoding/decoding: {e}")
            exist_error = True
            continue

    assert not exist_error, "Some codecs failed during binary-file encoding/decoding."
