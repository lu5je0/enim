#!/usr/bin/python3
import argparse
import base64
import re
import sys

from PIL import Image


# 生成偶数image
def make_image_even(image):
    image = image.convert("RGBA")
    pixels = list(image.getdata())
    pixels = [(r >> 1 << 1, g >> 1 << 1, b >> 1 << 1, a >> 1 << 1) for r, g, b, a in pixels]
    even_image = Image.new(image.mode, image.size)
    even_image.putdata(pixels)
    return even_image


def encode_byte(text):
    byte_str = bytearray(text, encoding="utf8")
    binary_list = [const_len_bin(i) for i in byte_str]
    return "".join(binary_list)


# 生成定长8位二进制数
def const_len_bin(num):
    bin_str = bin(num)
    return "0" * (10 - len(bin_str)) + bin_str[2:]


def decode_byte(byte_arr):
    if len(byte_arr) % 8 != 0:
        print("error")
        return
    pattern = re.compile(".{8}")
    str_list = [chr(int(x, 2)) for x in pattern.findall(byte_arr)]
    return "".join(str_list)


def encode_image(image, text):
    image = make_image_even(image)
    binary_arr = encode_byte(text)
    pixels = list(map(list, image.getdata()))
    for index, bit in enumerate(binary_arr):
        r_i = index // 4
        l_i = index % 4
        pixels[r_i][l_i] += int(bit)
    pixels = list(map(tuple, pixels))
    image = Image.new(image.mode, image.size)
    image.putdata(pixels)
    return image


def decode_image(image):
    pixels = image.getdata()
    binary_list = [str(r & 1) + str(g & 1) + str(b & 1) + str(a & 1) for r, g, b, a in pixels]
    binary_str = "".join(binary_list)
    # find的位置可能不为8的倍数,补全到8的倍数
    end_index = binary_str.find("000000000000") // 8 * 8 + 8
    return decode_byte(binary_str[:end_index])


parser = argparse.ArgumentParser()
parser.add_argument("img")
parser.add_argument("-t", "--text", default="")
parser.add_argument("-o", "--output", default="encoded.png")
parser.add_argument("-x", action="store_true", dest="decode", default=False)


def init():
    options = parser.parse_args()
    if options.decode:
        # 最后进行base64解码
        print(base64.b64decode(decode_image(Image.open(options.img))).decode('utf8'), end="")
    else:
        img = Image.open(options.img)
        # 判断是否有管道数据,base64编码
        if not sys.stdin.isatty():
            text_bs64 = base64.b64encode(sys.stdin.read().encode("utf8"))
        else:
            text_bs64 = base64.b64encode(options.text.encode("utf8"))
        img_encode = encode_image(img, text_bs64.decode("utf8"))
        img_encode.save(options.output)
        print("done")


if __name__ == "__main__":
    init()
