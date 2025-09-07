from ursina import *


def convertToColor(hex: str):
    hex = hex.removeprefix("#")
    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)
    return color.rgb32(r, g, b)
