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
from Queue import Queue
import threading
from urllib import quote
from util import post_process_for_socialblade

reload(sys)
sys.setdefaultencoding('utf8')


class DomainTask():
    def __init__(self, domain):
        para_dict = self._get_para(domain)
        self.downloader = Downloader(para_dict['downloader'])
        self.hub_extractor = HubExtractor(para_dict['hub_extractor'])
        self.detail_extractor = DetailExtractor(para_dict['detail_extractor'])
        self.file_path = para_dict['file_path']
        if not self.file_path.get('dir'):
            self.file_path['dir'] = './data/%s' % domain
        if not os.path.exists(self.file_path['dir']):
            os.mkdir(self.file_path['dir'])

    def _get_para(self, domain):
        lines = (line.strip() for line in open('./conf/' + domain + '.conf', 'r'))
        cur_para_info = {}
        para_dict = {}
        current_para = 'downloader'
        for line in lines:
            line = line.strip()
            if line.endswith("-->"):
                para_dict[current_para] = cur_para_info
                cur_para_info = dict()
                current_para = line[:-3]
            fields = line.split(':')
            if len(fields) < 2:
                continue
            key = fields[0]
            value = ':'.join(fields[1:])
            keys = key.split('.')
            if len(keys) > 1:
                if keys[0] not in cur_para_info:
                    cur_para_info[keys[0]] = dict()
                cur_para_info[keys[0]][keys[1]] = value
            else:
                cur_para_info[key] = value
        para_dict[current_para] = cur_para_info
        for key in para_dict:
            para_dict[key]['domain'] = domain
        return para_dict


def deep_first_processor(domain, entry_type='hub'):
    logging.info("*********proessing domain[%s]*********" % domain)
    doc = DomainTask(domain)
    tasks = task_dict[domain]
    for i, task in enumerate(tasks):
        try:
            if entry_type == 'hub':
                hub = doc.downloader.download(task)
                urls = doc.hub_extractor.extract_hub_page(hub)
            else:
                urls = [task]
            queue = Queue()
            for url in urls:
                queue.put(url)
            logging.info('processing domain[%s] hub [%s], [%d] left' % (domain, task, len(tasks) - i))
            while not queue.empty():
                url = queue.get()
                try:
                    logging.info('processing detail [%s], [%d] left' % (url, queue.qsize()))
                    de = doc.downloader.download(url)
                    #pdb.set_trace()
                    corpus = doc.detail_extractor.extract_detail_page(de, url)
                    if not corpus.get("content"):
                        time.sleep(1)
                        continue
                    next_page = corpus.get('next_page')
                    if next_page:
                        queue.put(corpus.get('next_page'))
                    file_name = get_name_form_url(url)
                    article_file = doc.file_path['dir'] + '/' + file_name
                    write_corpus_into_file(article_file, corpus)
                    #pdb.set_trace()
                    if domain == 'socialblade':
                        extra_crawler_socialblade(doc, corpus["para_special"])
                    time.sleep(1)
                except Exception as e:
                    logging.error(
                        "processing domain[%s], hub[%s], detail:[%s] failed for [%s]" % (domain, task, url, e))

        except Exception as e:
            logging.error("processing domain[%s], %s:[%s] failed for [%s]" % (domain, entry_type, task, e))


def extra_crawler_socialblade(doc, level2_urls):
    for level2_url in level2_urls:
        #pdb.set_trace()
        level2_page = doc.downloader.download(level2_url)

        corpus = doc.detail_extractor.extract_detail_page(level2_page, level2_url,  content_xpath= './/div[@id="YouTubeUserTopInfoBlock"]/div[@class="YouTubeUserTopInfo"]|.//div[@style="width: 860px; float: left; font-size: 8pt;"]',para_xpath= "")
        level3_url = level2_url + "/futureprojections"
        level3_page = doc.downloader.download(level3_url)

        corpus2 = doc.detail_extractor.extract_detail_page(level3_page, level3_url, content_xpath='//div[@style="width: 900px; float: left;"]', para_xpath= "")
        corpus["content"] += "\n------->>>>>>>\n" + corpus2["content"]
        article_file = doc.file_path['dir'] + '/userdata/' + get_name_form_url(level2_url)
        write_corpus_into_file(article_file, corpus)


def main(run_once=False):
    while True:
        time_stru = time.localtime(time.time())
        if not run_once and not (time_stru.tm_hour == 17 and time_stru.tm_min == 46):
            time.sleep(30)
            continue
        workers = [threading.Thread(target=deep_first_processor, args=(domain,)) for domain in task_dict]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()


if __name__ == '__main__':
    init_log()
    deep_first_processor('socialblade', 'detail')
    post_process_for_socialblade("./data/socialblade/")
    # if len(sys.argv)<2:
    #     main(run_once=True)
    # else:
    #     deep_first_processor('youdao','detail')
