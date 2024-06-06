import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from instances import ImgEncoder, ImgDecoder

def test_imgEncoder():
    text_path = r'G:\Project\test\寻找走丢的舰娘(34653).txt'
    image_path_grey = r'G:\Project\test\寻找走丢的舰娘(34653)(grey).png'
    image_path_rgba = r'G:\Project\test\寻找走丢的舰娘(34653)(rgba).png'
    image_path_rgba_full = r'G:\Project\test\寻找走丢的舰娘(34653)(rgba_full).png'

    # 编码
    encoder = ImgEncoder()
    encoder.encode_text(text_path, mode='grey')
    encoder.encode_text(text_path, mode='rgba')
    encoder.encode_text(text_path, mode='rgba_full')
    
    # 解码
    decoder = ImgDecoder()
    decoder.decode_image(image_path_grey, mode='grey')
    decoder.decode_image(image_path_rgba, mode='rgba')
    decoder.decode_image(image_path_rgba_full, mode='rgba_full')
