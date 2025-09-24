import pytest, logging
from celestialvault.instances.inst_imgEncoder import ImgEncoder, ImgDecoder

def test_imgEncoder():
    text_path = r"Q:\Project\test\text\test.txt"
    image_path_1bit = text_path.replace('.txt', '(1bit).png')
    image_path_morandi = text_path.replace('.txt', '(morandi).png')
    image_path_grey = text_path.replace('.txt', '(grey).png')
    image_path_rgb = text_path.replace('.txt', '(rgb).png')
    image_path_rgba = text_path.replace('.txt', '(rgba).png')
    image_path_rgb_redundancy = text_path.replace('.txt', '(rgb_redundancy).png')
    image_path_rgba_redundancy = text_path.replace('.txt', '(rgba_redundancy).png')

    # 编码
    encoder = ImgEncoder()
    encoder.encode_text_file(text_path, mode='1bit')
    encoder.encode_text_file(text_path, mode='morandi')
    encoder.encode_text_file(text_path, mode='grey')
    encoder.encode_text_file(text_path, mode='rgb')
    encoder.encode_text_file(text_path, mode='rgba')
    encoder.encode_text_file(text_path, mode='rgb_redundancy')
    encoder.encode_text_file(text_path, mode='rgba_redundancy')
    print("="*50)
    
    # 解码
    decoder = ImgDecoder()
    decoder.decode_image_file(image_path_morandi, mode='morandi')
    decoder.decode_image_file(image_path_1bit, mode='1bit')
    decoder.decode_image_file(image_path_grey, mode='grey')
    decoder.decode_image_file(image_path_rgb, mode='rgb')
    decoder.decode_image_file(image_path_rgba, mode='rgba')
    decoder.decode_image_file(image_path_rgb_redundancy, mode='rgb_redundancy')
    decoder.decode_image_file(image_path_rgba_redundancy, mode='rgba_redundancy')
