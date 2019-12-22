"""
@file:tran_maoyan.py
@time:2019/12/16-20:13
"""
import io
import re

import requests
from fontTools.ttLib import TTFont


class MaoYanKnn:
    def __init__(self, response):
        self.response = response
        self.standard_font = "./common/standard_one.woff"
        self.word_list = ['1', '9', '0', '5', '3', '6', '7', '2', '4', '8']

    def get_font_content(self):
        """
        :return:原始自定义字体的二进制文件内容
        """
        new_font_url = re.findall(r"format\('embedded-opentype'\).*?url\('(.*?)'\)", self.response, re.S)
        assert len(new_font_url) > 0, "Not Found Font File"
        b_font = requests.get("https:" + new_font_url[0]).content

        return b_font

    @staticmethod
    def get_font_coordinate_list(font_obj, uni_list):
        """
        获取字体文件的坐标信息列表
        :param font_obj: 字体文件对象
        :param uni_list: 总体文件包含字体的编码列表或元祖
        :return: 字体文件所包含字体的坐标信息列表
        """
        font_coordinate_list = list()
        for uni in uni_list:
            # 每一个字的GlyphCoordinates对象，包含所有文字连线位置坐标（x,y）元组信息
            word_glyph = font_obj['glyf'][uni].coordinates
            # 将元组转化为列表
            coordinate_list = list(word_glyph)
            # 汇总所有文字坐标信息
            font_coordinate_list.append(coordinate_list)

        return font_coordinate_list

    @staticmethod
    def comparison(coordinate1, coordinate2):
        """
        对比单个新字体和基准字体的坐标差值，若差值在设定范围变化则返回True，否则False
        :param coordinate1: 单字体1的坐标信息
        :param coordinate2: 单字体2的坐标信息
        :return: True或False
        """
        if len(coordinate1) != len(coordinate2):
            return False
        for i in range(len(coordinate1)):
            if abs(coordinate1[i][0] - coordinate2[i][0]) < 50 and abs(coordinate2[i][1] - coordinate2[i][1]) < 50:
                pass
            else:
                return False

            return True

    def get_new_font_dict(self):
        """
        用初始化的传入的基准字体和新字体文件对比，得到新字体文件编码与真实文字的映射。
        :return: 新字体文件中原编码与实际文字的映射字典
        """
        standard_font = TTFont(self.standard_font)
        # ['x', 'uniE01D', 'uniE70B', 'uniEDB9', 'uniE6D2', 'uniF5E8', 'uniE17E', 'uniF359', 'uniE3B4', 'uniE88D', 'uniE086']
        uni_tuple = standard_font.getGlyphOrder()[2:]
        # 获取基准字体坐标库
        standard_coordinate_list = self.get_font_coordinate_list(standard_font, uni_tuple)
        print(f"standard_coordinate_list is {standard_coordinate_list}")

        # 下载获取当前自定义字体的二进制文件
        b_font = self.get_font_content()
        # with open("my.woff", "wb") as f:
        #     f.write(b_font)
        # 将二进制文件当做文件操作
        new_font = TTFont(io.BytesIO(b_font))
        # 读取新字体坐标,去除第一个空值
        uni_list2 = new_font.getGlyphOrder()[2:]
        # 获取新字体坐标库
        new_coordinate_list = self.get_font_coordinate_list(new_font, uni_list2)
        print(f"new_coordinate_list:{new_coordinate_list}")

        new_font_dict = dict()
        # 比较基准字体和新字体坐标，映射新字体对应文字
        for nc_index, ncd in enumerate(new_coordinate_list):
            for sc_index, scd in enumerate(standard_coordinate_list):

                if self.comparison(scd, ncd):
                    new_font_dict[uni_list2[nc_index]] = self.word_list[sc_index]

        return new_font_dict

    def replace_response_font(self):
        new_font_dict = self.get_new_font_dict()
        # new_response = self.response
        print("new_font:", new_font_dict)

        # for key, value in new_font_dict.items():
        #     print(key, value)
        #     key_ = key.lower().replace('uni', "<span style='font-family: myfont;'>&#x") + ';</span>'
        #     # key_ = key.lower().replace('uni', "&#x") + ';'
        #     # 替换原网页中所有对应的key为实际数值value
        #     if key_ in self.response:
        #         new_response = new_response.replace(key_, str(value))

        # return new_response

    def __call__(self):
        return self.replace_response_font()
