# -*- coding:utf-8 -*-
import sys

import pdb
import re
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf8')


class HubExtractor():
    def __init__(self, para_info):
        self.para_dict = para_info

    def extract_hub_page(self, hub_page):
        try:
            html_tree = etree.HTML(hub_page.decode('utf-8'))
        except UnicodeDecodeError as ue:
            html_tree = etree.HTML(hub_page.decode('gbk'))
        if self.para_dict.get("drop_xpath"):
            for bad in html_tree.xpath(self.para_dict.get("drop_xpath")):
                bad.getparent().remove(bad)
        articles = set()
        nodes = html_tree.xpath(self.para_dict.get("url_xpath"))
        url_pattern = re.compile(self.para_dict.get("url_regex")) if self.para_dict.get("url_regex") else None
        for node in nodes:
            url = node.attrib.get('href')
            if url and not url.startswith("http"):
                url = self.para_dict.get("base_url") + url
            if not url_pattern or url_pattern.match(url):
                articles.add(url)
                # print url
        articles = post_url_processor(articles, self.para_dict.get("domain"))
        return articles


# url后处理（特殊逻辑）
def post_url_processor(urls, domain):
    if domain == 'ftchinese':
        new_urls = []
        for url in urls:
            groups = re.findall("(http://www.ftchinese.com/story/\d+)", url)
            if groups:
                new_urls.append(groups[0] + "/ce#adchannelID=1100")
        return new_urls
    elif domain == 'yiyan':
        new_urls = []
        for url in urls:
            groups = re.findall("http://article.yeeyan.org/view/\d+/(\d+)", url)
            if groups:
                new_urls.append("http://article.yeeyan.org/compare/%s" % groups[0])
        return new_urls
    else:
        return urls
