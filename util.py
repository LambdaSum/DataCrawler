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


def delete_empty_file(dir=None):
    dir = dir if dir else './data/processed/'
    files = os.listdir(dir)
    for file in files:
        try:
            if os.path.getsize(dir + "/" + file) == 0:  # 得到文件大小，如果是目录返回0
                os.remove(dir + "/" + file)
                print(file + " deleted")
        except Exception as e:
            logging.error('processing file:%s error for:%s' % (file, e))


def delete_oneline_file(dir=None):
    dir = dir if dir else './data/processed/'
    files = os.listdir(dir)
    for file in files:
        try:
            line_num = 0
            for line in open(dir + '/' + file, 'r'):
                if line != '\n':
                    line_num += 1
            if line_num < 2:
                os.remove(dir + "/" + file)
                print(file + " deleted")
        except Exception as e:
            logging.error('processing file:%s error for:%s' % (file, e))


def language_classify(text):
    for i in text.decode('utf8'):
        if u'\u4e00' < i < u'\u9fa5':
            return '0'
    return '1'


def delete_eng():
    aa = {}
    with open("chs", 'r+')as e:
        aa = json.loads(e.read())
        for a in aa.keys():
            if language_classify(a) == '1':
                aa.pop(a)
        print len(aa.keys())
    with open('chs2', 'w') as e:
        e.write(json.dumps(aa))


def arrange_data(dir='./data/hujiang/'):
    files = os.listdir(dir)
    hubfp = open('hub', 'a')
    for file in files:
        try:
            fp = open(dir + '/' + file, 'r')
            new_fp = open("./data/yiyan2/" + file, 'w')
            line = fp.readline()
            if language_classify(line) == '0':
                line = fp.readline()
            temp_line = ''
            while line:
                pre_line = line
                temp_line += pre_line.replace('\n', '')
                line = fp.readline()
                if language_classify(temp_line) != language_classify(line):
                    new_fp.write(temp_line.replace('\r', '') + '\n')
                    temp_line = ''
            new_fp.close()
            fp.close()
        except Exception as e:
            logging.error('processing file:%s error for:%s' % (file, e))
            hubfp.write(file + '\n')


def empty_line(dir='./data/yiyan/'):
    files = os.listdir(dir)
    hubfp = open('hub', 'a')
    for file in files:
        # pdb.set_trace()
        article = ''
        try:
            fp = open(dir + '/' + file, 'r')
            new_fp = open("./data/yiyan2/" + file, 'w')
            line = fp.readline()
            while line:
                if line.replace('\r', '') == '\n':
                    line = fp.readline()
                    continue
                article += line.replace('\r', '').replace('+', ' ')
                # for sentence in re.:

                line = fp.readline()
            # pdb.set_trace()
            new_fp.write(article)
            new_fp.close()
            fp.close()
        except Exception as e:
            logging.error('processing file:%s error for:%s' % (file, e))
            hubfp.write(file + '\n')


def arrange_data3(dir='./data/processed/'):
    files = os.listdir(dir)
    hubfp = open('hub', 'a')
    new_fp = open("./data/all.data", 'w')
    for file in files:
        try:
            fp = open(dir + '/' + file, 'r')
            line = fp.read().split("\n")
            while line:
                if line == ('\n'):
                    continue
                new_fp.write(line)
                line = fp.readline()
            fp.close()
        except Exception as e:
            logging.error('processing file:%s error for:%s' % (file, e))
            hubfp.write(file + '\n')
    new_fp.close()


def process_data(dir='./data/kekenet/', first_line='1', forbiden_words=['adsbygoogle', '来源', '摘要', '中文译文']):
    files = os.listdir(dir)
    hubfp = open('hub', 'a')

    def move(fp, pre_line='', line='', step=1):
        for i in range(step):
            pre_line = line
            line = fp.readline()
            while line and not line.strip():
                line = fp.readline()
        return pre_line, line

    for file in files:
        print 'writing %s' % file
        try:
            fp = open(dir + '/' + file, 'r')
            new_fp = open("./data/test/" + file, 'w')
            pre_line, line = move(fp, "", fp.readline(), 1)
            while pre_line and line:
                for word in forbiden_words:
                    if word in pre_line:
                        pre_line, line = move(fp, pre_line, line, 1)
                    elif word in line:
                        line = fp.readline()
                if language_classify(pre_line) == first_line != language_classify(line):
                    if 0.3 < (len(pre_line) * 1.0 / len(line)) < 3:
                        new_fp.write(pre_line.replace('\n', '') + '\n')
                        new_fp.write(line.replace('\n', '') + '\n')
                    pre_line, line = move(fp, pre_line, line, 2)
                else:
                    pre_line, line = move(fp, pre_line, line, 1)
            new_fp.close()
            fp.close()
        except Exception as e:
            logging.error('processing file:%s error for:%s' % (file, e))
            hubfp.write(file + '\n')


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


def get_processed_names(file_path):
    files = os.listdir(file_path)
    key_words = []
    for file in files:
        word = re.findall('http___dict.youdao.com_example_blng_jap_(.*)_#keyfrom=dict.main', file)
        if word:
            key_words.append(unquote(word[0]).decode("utf8"))

    return key_words


def read_history_pages(file_path):
    if not os.path.isfile(file_path):
        write_history_pages(file_path, [])

    with open(file_path, 'r') as fp:
        data = fp.read()
        list = json.loads(data) if data else []
        return set(list)


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
