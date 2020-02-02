import io
import re
import itertools

import requests

from fontTools.ttLib import TTFont
from scrapy import Selector
from urllib.parse import urljoin
from spider.util.knn_font import Classify


class KnnMaoYan:
    def __init__(self):
        self.indexUrl = "https://maoyan.com/board/6"
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.obj = Classify()

    def sub_text(self, url):
        resp = requests.get(url=url, headers=self.headers)
        text = resp.text
        b_font = self.get_font_content(text)

        new_font = TTFont(io.BytesIO(b_font))
        # 读取新字体坐标,去除第一个空值
        glyf_order = new_font.getGlyphOrder()[2:]
        font_coordinate_list = self.get_font_coordinate_list(new_font, glyf_order)
        map_dict = self.get_map(font_coordinate_list, glyf_order)

        for uni in map_dict.keys():
            text = text.replace(uni, map_dict[uni])

        return text

    def outputUrls(self):
        resp = requests.get(url=self.indexUrl, headers=self.headers)
        response = Selector(text=resp.text)

        detail_urls = response.xpath("//dl[@class='board-wrapper']/dd/a/@href").extract()
        if detail_urls:
            return detail_urls
        else:
            raise

    def run(self, durl):
        url = urljoin(self.indexUrl, durl)
        text = self.sub_text(url)
        response = Selector(text=text)
        name = response.xpath("//*[@class='name']/text()").extract_first().strip()

        score = response.xpath("//span[@class='index-left info-num ']/span/text()").extract_first()

        boxoffice = response.xpath("//div[@class='movie-index-content box']/span[1]/text()").extract_first()

        unit = response.xpath("//div[@class='movie-index-content box']/span[2]/text()").extract_first("")

        boxunit = boxoffice + unit
        return name, score, boxunit

    def get_map(self, font_coordinate_list, glyf_order):
        """

        :param uni_list:
        :return:
        """
        map_li = map(lambda x: str(int(x)), self.obj.knn_predict(font_coordinate_list))

        uni_li = map(lambda x: x.lower().replace('uni', '&#x') + ';', glyf_order)

        return dict(zip(uni_li, map_li))

    def get_font_content(self, response):
        """
        :return:原始自定义字体的二进制文件内容
        """
        new_font_url = re.findall(r"format\('embedded-opentype'\).*?url\('(.*?)'\)", response, re.S)
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
            # 每个字的GlyphCoordinates对象，包含连线位置坐标（x,y）元组信息
            word_glyph = font_obj['glyf'][uni].coordinates
            # 将[(147, 151), (154, 89),]转化为[ ,]
            coordinate_list = list(itertools.chain(*word_glyph))
            # 汇总所有文字坐标信息
            font_coordinate_list.append(coordinate_list)

        return font_coordinate_list
