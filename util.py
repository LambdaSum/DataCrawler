#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2017/2/21 17:32
# @Author: lambdali

import logging
import os
import re
import pdb
import json
from urllib import unquote, quote
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def write_corpus_into_file(file, corpus):
    try:
        with open(file, 'w') as wfp:
            article = corpus['url']
            article += "\n" + corpus['content']
            wfp.write(article)
    except Exception as e:
        logging.error('write file:[%s] failed for [%s]' % (file, e))


def post_process_for_socialblade(file_path):
    files = os.listdir(file_path)
    header = {"5000": "RANK\tSB SCORE\tUSER\tNETWORK\tWEBSITE\tSUBSCRIBERS\tVIDEO VIEWS\n",
              "networks": "RANK\tNETWORK\tWEBSITE\tMEMBERS\t•SUBSCRIBERS (LAST 30 DAYS)•\tVIDEO VIEWS (LAST 30 DAYS)\n",
              "jp": "RANK\tSB SCORE\tUSER\tNETWORK\tWEBSITE\tSUBSCRIBERS\tVIDEO VIEWS\n",
              "br": "RANK\tSB SCORE\tUSER\tNETWORK\tWEBSITE\tSUBSCRIBERS\tVIDEO VIEWS\n",
              "gb": "RANK\tSB SCORE\tUSER\tNETWORK\tWEBSITE\tSUBSCRIBERS\tVIDEO VIEWS\n",
              "us": "RANK\tSB SCORE\tUSER\tNETWORK\tWEBSITE\tSUBSCRIBERS\tVIDEO VIEWS\n",
              "kr": "RANK\tSB SCORE\tUSER\tNETWORK\tWEBSITE\tSUBSCRIBERS\tVIDEO VIEWS\n",
              }
    for file in files:
        if file.endswith("csv"):
            continue
        cat = file[file.rfind('_') + 1:]
        pdb.set_trace()
        cols = len(header[cat].split("\t"))
        article = header[cat]
        with open(file_path + '/' + file, 'r') as fp:
            lines = fp.readlines()

            for i in xrange(1, len(lines)):
                splitor = '\t'
                if i % (cols) == 0:
                    splitor = '\n'
                article += lines[i].strip() + splitor

        with open(file_path + '/' + file + '.csv', 'w') as fp:
            fp.write(article)



def get_name_form_url(url):
    aa = re.sub(r"[/\\:*?\"<>|]", "_", url)
    if aa == '_':
        pdb.set_trace()
    return aa


def write_history_pages(file_path, list):
    if not list and os.path.isfile(file_path):
        return
    with open(file_path, 'w') as wfp:
        data = json.dumps(list)
        wfp.write(data)


def init_log():
    log_path = './crawler.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        filename=log_path,
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)


if __name__ == '__main__':
    with open("text", 'r')as fp:
        lines = fp.readlines()
        myset = set()
        list = ""
        files = os.listdir("./data/socialblade/userdata/")
        for line in lines:
            myset.add(line.strip())
        for web in myset:
            if get_name_form_url(web) not in files:
                list += web + '\n'
        print len(list)
        with open("ramain", "w") as wfp:
            wfp.write(list)
