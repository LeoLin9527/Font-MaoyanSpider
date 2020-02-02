"""
@file:woff_to_xml.py
@time:2019/12/18-22:04
"""
from fontTools.ttLib import TTFont

from spider.util.get_train_font import get_font_data

if __name__ == '__main__':
    option = input("输入操作类型:")
    if option == '1':
        base_font = TTFont('../../common/standard_one.woff')
        # 获取编码
        glyf_order = base_font.getGlyphOrder()[2:]
        base_font.saveXML('./common/standard_one.xml')

        base_font = TTFont('../../common/standard_two.woff')
        base_font.saveXML('./common/standard_two.xml')

    if option == '2':
        get_font_data()
