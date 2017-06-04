# -*- coding:utf-8 -*-
import sys
import os
import pdb
import time
from db_util import MyDbHelper


class DataDumper:
    def __init__(self):
        self.db_helper = MyDbHelper()

    def dumps(self, file_type, file_path, date):
        self.get_data_from_file(file_type, file_path)

    def get_data_from_file(self, file_type, file_path):
        result_dict = {}
        with open(file_path, 'r') as fp:
            content = fp.read()
        if file_type == 'country':
            lines = content.split("\n")[1:]
            country_result = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                column = i % 7
                if column == 0:
                    rank = lines[i]
                elif column == 1:
                    sb_score = lines[i]
                elif column == 2:
                    grade = lines[i]
                elif column == 3:
                    channel = lines[i]
                elif column == 4:
                    channel_url = lines[i]
                elif column == 5:
                    website = lines[i]
                elif column == 6:
                    subscribers = lines[i]
                    country_result.append(rank, sb_score, grade, channel, channel_url, website, subscribers)
            result_dict["country"] = country_result
        elif file_type == 'userdata':
            paras = content.split(">>>>>>>>>>")

            for para in paras:
                if para.startswith("https://socialblade.com/"):
                    user_url = para.strip()
                    continue
                lines = para.split("\n")
                if para.startswith('->'):
                    para_id = lines[0][2:].strip()
                    if para_id == "user_info":
                        i = 1
                        while True:
                            line = lines[i]
                            if line.startswith("Uploads"):
                                i += 1
                                uploads = lines[i]
                            elif line.startswith("Subscribers"):
                                i += 1
                                subscribers = lines[i]
                            elif line.startswith("Video"):
                                i += 1
                                views = lines[i]
                            elif line.startswith("Channel"):
                                i += 1
                                channel_type = lines[i]
                            elif line.startswith("User Created"):
                                created = lines[i][12:]
                    elif para_id == "30days_view_info":
                        days_30_views_add = lines[1].strip()
                        days_30_views_addrate = lines[2].strip()
                    elif para_id == "30days_view_extrainfo":
                        if "up" in lines[1]:
                            days_30_views_addrate = "-" + days_30_views_addrate
                    elif para_id == "30days_sub_info":
                        days_30_subs_add = lines[1].strip()
                        days_30_subs_addrate = lines[1].strip()
                    elif para_id == "30days_sub_extrainfo":
                        if "down" in lines[1]:
                            days_30_subs_addrate = "-" + days_30_subs_addrate
                    elif para_id == "monthly_table":
                        monthly_table = []
                        for i, line in enumerate(lines[1:]):
                            line = line.strip()
                            if not line:
                                continue
                            column = i % 7
                            if column == 0:
                                date = lines[i]
                            elif column == 1:
                                week = lines[i]
                            elif column == 2:
                                subscribers_daily_add = lines[i]
                            elif column == 3:
                                subscribers_sum = lines[i]
                            elif column == 4:
                                views_daily_add = lines[i]
                            elif column == 5:
                                views_sum = lines[i]
                            elif column == 6:
                                estimated_earnings = lines[i]
                                temp = (date, week, subscribers_daily_add, subscribers_sum, views_daily_add, views_sum,
                                        estimated_earnings)
                                monthly_table.append(temp)
                        result_dict["monthly_table"] = monthly_table
                    elif para_id == "future_pro":
                        future_pro_result = []
                        i = 0
                        for line in lines[1]:
                            if not line.strip() or line.startswith("https://socialblade.com"):
                                continue
                            else:
                                i += 1
                            column = i % 4
                            if column == 0:
                                cur_date = line.strip()
                            elif column == 1:
                                time_until = line.strip()
                            elif column == 2:
                                subs_prediction = line.strip()
                            elif column == 3:
                                views_prediction = line.strip()
                                temp = (cur_date, time_until, subs_prediction, views_prediction)
                                future_pro_result.append(temp)
                        result_dict['future_pro'] = future_pro_result
            result_dict["user_info"] = (
            user_url, uploads, subscribers, views, channel_type, created, days_30_views_add, days_30_views_addrate,
            days_30_subs_add, days_30_subs_addrate)


if __name__ == '__main__':
    dumper = DataDumper()
    base_dir = "./data/socialblade/"
    list = os.listdir(base_dir)
    pdb.set_trace()
    time.time()
    for file in list:
        if os.path.isdir(file):
            sublist = os.listdir(base_dir+file)
            for subfile in sublist:
                dumper.dumps("userdata", base_dir+file+"/"+subfile)
        dumper.dumps("country", base_dir+file)

    pdb.set_trace()
