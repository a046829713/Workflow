import requests
from bs4 import BeautifulSoup
from lxml import etree
import re


def fetch_country_names():
    """
        用來爬取所有國家的中英文名稱(目前沒有使用到)
    Returns:
        _type_: _description_
    """
    url = r'https://zh.wikipedia.org/zh-tw/%E4%B8%96%E7%95%8C%E6%94%BF%E5%8D%80%E7%B4%A2%E5%BC%95'
    response = requests.get(url)

    data = response.text
    html = etree.HTML(data)  # type: ignore
    filter_datas = html.xpath(
        "//table[not(@class)]//tr//td[2]/text() | //table[not(@class)]//tr//td[3]/text()")
    out_list = [i.strip() for i in filter_datas if i.strip()]

    # ('法屬玻里尼西亞', 'French Polynesia')
    filter_dict = {}
    pairs = list(zip(out_list[::2], out_list[1::2]))

    for _i in pairs:
        if _i[1] in filter_dict:
            continue
        else:
            filter_dict[_i[1]] = _i
    
    return [(i[0] + i[1], i[0] + i[1])for i in list(filter_dict.values())]


if __name__ == '__main__':
    print(fetch_country_names())
