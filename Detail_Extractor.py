# -*- coding:utf-8 -*-
import sys
import pycurl
from urllib import unquote, quote
import StringIO
import logging
import pdb
import re
from lxml import etree
from Downloader import Downloader
import pdb

reload(sys)
sys.setdefaultencoding('utf8')


class DetailExtractor:
    def __init__(self, para_info):
        self.para_info = para_info

    def extract_detail_page(self, detail_page, url):
        detail_page = detail_page.replace('<BR>', '\n').replace('<br>', '\n')
        try:
            html_tree = etree.HTML(detail_page.decode('utf-8'))
        except UnicodeDecodeError as ue:
            try:
                html_tree = etree.HTML(detail_page.decode('gbk'))
            except Exception as e:
                html_tree = etree.HTML(detail_page)
        corpus = dict()
        corpus['url'] = url
        if self.para_info.get("drop_xpath"):
            for bad in html_tree.xpath(self.para_info.get("drop_xpath")):
                bad.getparent().remove(bad)
        title_node = html_tree.xpath(self.para_info.get("title_xpath")) if self.para_info.get("title_xpath") else None
        title = title_node.text if title_node else None
        corpus['title'] = title
        contents = html_tree.xpath(self.para_info.get("content_xpath")) if self.para_info.get("content_xpath") else []
        article = ''
        if self.para_info.get("next_page"):
            next_page_node = html_tree.xpath(self.para_info['next_page'])
            if next_page_node:
                next_page = next_page_node[0].attrib.get('href')
                if not next_page.startswith('http'):
                    next_page = self.para_info['base_url'] + next_page
                corpus['next_page'] = next_page
        for content in contents:
            for node in content.xpath(self.para_info.get("para_xpath")):
                para = node.xpath('string(.)').strip()
                chars = para.split('\n')
                new_para = ""
                for char in chars:
                    if char.strip():
                        new_para += '\n' + char.strip()
                para = new_para.strip()
                # print etree.tostring(node)
                # pdb.set_trace()
                para_special = node.xpath(self.para_info.get("para_special")) if self.para_info.get(
                    "para_special") else []
                if len(para_special) and not para_special[0].startswith("http"):
                    para_special = [self.para_info['base_url'] + para_special[0]]
                para += "\n" + para_special[0] if len(para_special) else ""
                article += para + '\n' if para else ""
        if not contents:
            article = self.get_content_by_regex(detail_page)
        corpus['content'] = article
        return corpus

    def get_content_by_regex(self, input):
        if self.para_info.get('en_regex'):
            ch_matches = re.search(self.para_info.get('ch_regex'), input)
            ch = ""
            if ch_matches and len(ch_matches.groups()):
                ch = unquote(ch_matches.groups()[0]).replace('+', ' ')
            en_matches = re.search(self.para_info.get('en_regex'), input)
            en = ''
            if en_matches and len(en_matches.groups()):
                en = unquote(en_matches.groups()[0]).replace('+', ' ')
            return en + '\n-->\n' + ch
        return ''
