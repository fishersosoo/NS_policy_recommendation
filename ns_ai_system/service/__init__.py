# coding=utf-8
import re
def conert_ch2num(ch):
    ch=ch.strip("元")
    ch=ch.replace("万","0000")
    ch = ch.replace("千", "000")
    ch = ch.replace("百", "00")
    ch = ch.replace("十", "0")
    ch = ch.replace("亿", "000000000")
    return float(ch)

