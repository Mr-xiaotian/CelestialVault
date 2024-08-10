import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from instances.inst_imgEncoder import ImgEncoder, ImgDecoder

def test_imgEncoder():
    text_path = r'\\192.168.31.2\raid1_500G\Book\小说\H小说\test\斗破苍穹.txt'
    image_path_grey = text_path.replace('.txt', '(grey).png')
    image_path_rgb = text_path.replace('.txt', '(rgb).png')
    image_path_rgba = text_path.replace('.txt', '(rgba).png')
    image_path_grey_binary = text_path.replace('.txt', '(grey_binary).png')
    image_path_rgb_binary = text_path.replace('.txt', '(rgb_binary).png')
    image_path_rgba_binary = text_path.replace('.txt', '(rgba_binary).png')

    # 编码
    encoder = ImgEncoder()
    encoder.encode_text_file(text_path, mode='grey')
    encoder.encode_text_file(text_path, mode='rgb')
    encoder.encode_text_file(text_path, mode='rgba')
    encoder.encode_text_file(text_path, mode='grey_binary')
    encoder.encode_text_file(text_path, mode='rgb_binary')
    encoder.encode_text_file(text_path, mode='rgba_binary')
    print("="*50)
    
    # 解码
    decoder = ImgDecoder()
    decoder.decode_image_file(image_path_grey, mode='grey')
    decoder.decode_image_file(image_path_rgb, mode='rgb')
    decoder.decode_image_file(image_path_rgba, mode='rgba')
    decoder.decode_image_file(image_path_grey_binary, mode='grey_binary')
    decoder.decode_image_file(image_path_rgb_binary, mode='rgb_binary')
    decoder.decode_image_file(image_path_rgba_binary, mode='rgba_binary')
