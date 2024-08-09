import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from instances.inst_imgEncoder import ImgEncoder, ImgDecoder

def test_imgEncoder():
    text_path = r"Q:\Project\test\text_re\test.txt"
    image_path_grey = text_path.replace('.txt', '(grey).png')
    image_path_rgba = text_path.replace('.txt', '(rgba).png')
    image_path_rgba_full = text_path.replace('.txt', '(rgba_full).png')
    image_path_rgb = text_path.replace('.txt', '(rgb).png')

    # 编码
    encoder = ImgEncoder()
    encoder.encode_text(text_path, mode='grey')
    encoder.encode_text(text_path, mode='rgba')
    encoder.encode_text(text_path, mode='rgba_full')
    encoder.encode_text(text_path, mode='rgb')
    print("="*50)
    
    # 解码
    decoder = ImgDecoder()
    decoder.decode_image(image_path_grey, mode='grey')
    decoder.decode_image(image_path_rgba, mode='rgba')
    decoder.decode_image(image_path_rgba_full, mode='rgba_full')
    decoder.decode_image(image_path_rgb, mode='rgb')
