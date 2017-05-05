# -*- coding:utf-8 -*- 
import sys
import pycurl
import urllib
import StringIO
import logging
import certifi
from tornado_fetcher import Fetcher

reload(sys)
sys.setdefaultencoding('utf8')
G_HTTP_OK = 200
METHOD_POST = 'POST'
METHOD_GET = 'GET'


class Downloader:
    def __init__(self, para_dict):
        self.domain = para_dict.get('domain')
        self.curl_handel = pycurl.Curl()
        self.para_dict = para_dict
        self.post_para = para_dict.get('post_para')
        self.curl_handel.setopt(self.curl_handel.REFERER, self.para_dict['Referer'])
        self.curl_handel.setopt(pycurl.MAXREDIRS, 2)
        self.curl_handel.setopt(pycurl.CONNECTTIMEOUT, 20)
        self.curl_handel.setopt(pycurl.TIMEOUT, 50)
        self.curl_handel.setopt(pycurl.CAINFO, certifi.where())
        # self.curl_handel.setopt(pycurl.PROXY, "110.73.10.86")
        # self.curl_handel.setopt(pycurl.PROXYPORT, 8123)
        self.curl_handel.setopt(pycurl.FOLLOWLOCATION, 1)
        self.post_fields = {}
        self.curl_handel.setopt(pycurl.CUSTOMREQUEST, self.para_dict['Method'])
        # header_list = ["%s:%s"%(key, value) for key,value in para_dict['Header'].items()]
        contenttype = "Content-Type:%s" % (self.para_dict['Content-Type'])
        requestwith = "X-Requested-With:%s" % (self.para_dict['X-Requested-With'])
        # cookie = "Cookie:%s" % (self.para_dict['Cookie'])
        # print header_list
        # import pdb;pdb.set_trace()
        self.phantomjs_downloader = Fetcher()

        self.curl_handel.setopt(pycurl.HTTPHEADER, [contenttype,requestwith])
        self.curl_handel.setopt(pycurl.USERAGENT,
                                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36")
        if self.para_dict['Method'] == METHOD_POST:
            for (pk, pv) in self.post_para.items():
                self.post_fields.setdefault(pk, pv)

    def download(self, url, use_phantomjs=False):
        print '*******************\n'+url
        if use_phantomjs:
            content = self.phantomjs_downloader.phantomjs_fetch(url)
            return content
        output = StringIO.StringIO()
        output.truncate(0)
        output.seek(0)
        self.curl_handel.setopt(pycurl.URL, url)
        self.curl_handel.setopt(pycurl.WRITEFUNCTION, output.write)
        # set request parameter
        if self.para_dict['Method'] == METHOD_POST:
            self.curl_handel.setopt(self.curl_handel.POSTFIELDS, urllib.urlencode(self.post_fields))
        elif self.para_dict['Method'] == METHOD_GET:
            self.curl_handel.setopt(pycurl.URL, url)
        self.curl_handel.perform()
        ret = self.curl_handel.getinfo(self.curl_handel.HTTP_CODE)
        if ret != G_HTTP_OK:
            logging.error("[%s]http post error" % url)
        output_str = output.getvalue().strip()
        if len(output_str) == 0:
            logging.error("[%s]http response empty" % url)
        return output_str
