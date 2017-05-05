# -*- coding:utf-8 -*-
from urllib import quote, unquote
import json
import itertools
import random, pdb
from util import get_processed_names

task_dict = {
    'socialblade': ["https://socialblade.com/youtube/top/country/us",
                    "https://socialblade.com/youtube/top/5000",
                    "https://socialblade.com/youtube/top/networks",
                    "https://socialblade.com/youtube/top/country/gb",
                    "https://socialblade.com/youtube/top/country/jp",
                    "https://socialblade.com/youtube/top/country/kr",
                    "https://socialblade.com/youtube/top/country/br", ]
}
