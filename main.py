# -*- coding:utf-8 -*-
import sys
import os
import pdb
from Downloader import Downloader
from Hub_Extractor import HubExtractor
from Detail_Extractor import DetailExtractor
from util import init_log, write_corpus_into_file, get_name_form_url
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
            pdb.set_trace()
            while not queue.empty():
                url = queue.get()
                try:
                    logging.info('processing detail [%s], [%d] left' % (url, queue.qsize()))
                    de = doc.downloader.download(url)
                    # pdb.set_trace()
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
                    # pdb.set_trace()
                    if domain == 'socialblade':
                        extra_crawler_socialblade(doc, corpus["para_special"])
                    time.sleep(1)
                except Exception as e:
                    logging.error(
                        "processing domain[%s], hub[%s], detail:[%s] failed for [%s]" % (domain, task, url, e))
                    pdb.set_trace()
        except Exception as e:
            logging.error("processing domain[%s], %s:[%s] failed for [%s]" % (domain, entry_type, task, e))


def extra_crawler_socialblade(doc, level2_urls):
    base_url = 'https://socialblade.com'
    for i, level2_url in enumerate(level2_urls):
        logging.info('processing leve2_url[%s] , [%d] left' % (level2_url, len(level2_urls) - i))
        try:
            level2_page = doc.downloader.download(level2_url)
            main_corpus = doc.detail_extractor.extract_detail_page(level2_page, level2_url,
                                                                   xpath_dict={
                                                                       'video_stats': './/div[@id="YouTubeUserMenu"]/a[6]/@href',
                                                                       'month_stats': './/div[@id="YouTubeUserMenu"]/a[3]/@href',
                                                                       'future_pro': './/div[@id="YouTubeUserMenu"]/a[2]/@href',
                                                                       "user_info": './/div[@id="YouTubeUserTopInfoBlock"]/div[@class="YouTubeUserTopInfo"]',
                                                                       '30days_view_info': './/span[@id="afd-header-views-30d"]|.//span[@id="afd-header-views-30d-perc"]',
                                                                       '30days_view_extrainfo': './/span[@id="afd-header-views-30d-perc"]/span/i/@class',
                                                                       '30days_sub_info': './/span[@id = "afd-header-subs-30d"]|.//span[@id="afd-header-subs-30d-perc"]',
                                                                       '30days_sub_extrainfo': './/span[@id="afd-header-subs-30d-perc"]/span/i/@class'})
            article = ''
            for key in ['user_info', '30days_view_info', '30days_view_extrainfo', '30days_sub_info',
                        '30days_sub_extrainfo']:
                article += ">>>>>>>>>>->%s\n%s\n" % (key, main_corpus['xpath_content'][key])
            month_stats_url = base_url + main_corpus['xpath_content']["month_stats"]
            month_stats_page = doc.downloader.download(month_stats_url)
            month_stats_corpus = doc.detail_extractor.extract_detail_page(month_stats_page, month_stats_url,
                                                                          xpath_dict={
                                                                              'monthly_table': './/div[@style="width: 880px; float: left;"]/div[position()>4][position()<31]'})
            article += ">>>>>>>>>>->%s\n%s\n" % ('monthly_table', month_stats_corpus['xpath_content']['monthly_table'])

            future_pro_url = base_url + main_corpus['xpath_content']["future_pro"]
            future_pro_page = doc.downloader.download(future_pro_url)
            future_pro_corpus = doc.detail_extractor.extract_detail_page(future_pro_page, future_pro_url, xpath_dict={
                'future_pro': './/div[@style="width: 900px; float: left;"]/div[@class="TableMonthlyStats"]'})
            article += ">>>>>>>>>>->%s\n%s\n" % ('future_pro', future_pro_corpus['xpath_content']['future_pro'])

            pdb.set_trace()
            video_stats_url = base_url + main_corpus['xpath_content']["video_stats"]
            video_stats_page = doc.downloader.download(video_stats_url, use_phantomjs=True)
            video_stats_corpus = doc.detail_extractor.extract_detail_page(video_stats_page, video_stats_url,
                                                                          xpath_dict={
                                                                              'video_table': './/div[@class="RowRecentTable"]'})
            article += ">>>>>>>>>>->%s\n%s\n" % ('video_table', video_stats_corpus['xpath_content']['video_table'])

            main_corpus["content"] = article
            article_file = doc.file_path['dir'] + '/userdata/' + get_name_form_url(level2_url)
            write_corpus_into_file(article_file, main_corpus)
        except Exception as e:
            logging.error("processing level2url[%s] failed for [%s]" % (level2_url, e))


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


def test(domain):
    doc = DomainTask(domain)
    url = 'https://www.youtube.com/watch?v=3cJvnYx3jRA'
    content = doc.downloader.download(url=url, use_phantomjs=True)
    pdb.set_trace()
    corpus = doc.detail_extractor.extract_detail_page(content, url,
                                                      xpath_dict={'watch': './/div[@id="watch7-views-info"]'})
    pdb.set_trace()


if __name__ == '__main__':
    # test('socialblade')
    init_log()
    deep_first_processor('socialblade', 'detail')
    # post_process_for_socialblade("./data/socialblade/")
    # if len(sys.argv)<2:
    #     main(run_once=True)
    # else:
    #     deep_first_processor('youdao','detail')
