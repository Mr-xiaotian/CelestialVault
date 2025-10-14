import pytest, logging

from celestialvault.instances.inst_imgcodecs import CODEC_REGISTRY


def test_codecs_text():
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
