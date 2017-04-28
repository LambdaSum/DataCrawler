# -*- coding:utf-8 -*-
import sys
import os
import pdb
from Downloader import Downloader
from Hub_Extractor import HubExtractor
from Detail_Extractor import DetailExtractor
from util import init_log, write_corpus_into_file, read_history_pages, write_history_pages, get_name_form_url
from task import task_dict
import logging
import time
import json
import re
from Queue import Queue
import threading
from main import DomainTask

reload(sys)
sys.setdefaultencoding('utf8')


def get_url_and_content(file):
    with open(file, 'rb') as fp:
        content = fp.read()
        pages = []
        splits = content.split('<html>')
        if not splits:
            splits = content.split("<!DOCTYPE html>")
        for split in splits:
            end = split.find('</html>')
            if end > 0:
                pages.append("<html>" + split[:end - 1] + "</html>")
        return pages


def domain_extractor(domain, dir='./data2'):
    logging.info("*********proessing domain[%s]*********" % domain)
    doc = DomainTask(domain)
    files = os.listdir(dir)
    i = 0
    for file in files:
        try:
            i += 1
            logging.info('processing domain[%s] [%d] left' % (domain, len(files) - i))
            pages = get_url_and_content(dir + "/" + file)
            for num, page in enumerate(pages):
                try:
                    corpus = doc.detail_extractor.extract_detail_page(page, "null")
                    if not corpus.get("content"):
                        continue
                    file_name = num
                    article_file = doc.file_path['dir'] + '/' + file + "_" + str(file_name)
                    write_corpus_into_file(article_file, corpus)

                except Exception as e:
                    logging.error('prcessing file[%s] page[%d] failed for[%s]' % (file, num, e))
        except Exception as e:
            logging.error('prcessing file[%s]failed for[%s]' % (file, e))


if __name__ == '__main__':
    init_log()
    domain_extractor('jukuu')
