#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

import sys
import redis
import struct, socket
from datetime import datetime
import csv
sys.path.append('../../')
from put_in_redis import Entry


# CONFIG #
dataset = "blackhole27"
THRESHOLD_IGNORE = 100
BLACKHOLE_ADDRESS = "xxx.xxx.xxx.xxx"
windowS = datetime(2017, 2, 1, 0, 0, 0)
windowE = datetime(2017, 2, 1, 1, 0, 0)

# REDIS #
serv_all = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=10)
serv_ip_matching_isn = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=7)

def compute_then_make_stat():
    
    all_keys = serv_all.keys(dataset+":20"+"*")

    timestamp_window = []
    isn_dico = {}

    iter_num = 0
    for day_num, ip_day in enumerate(all_keys):
        if(iter_num % int(1) == 0):
            print("progress: {}%".format(int(iter_num/len(all_keys)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        format_date = ip_day.decode().split(":")[1]
        for entry_json in serv_all.smembers(ip_day):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
            timestamp = float(entry.timestamp)
            isn = int(entry.isn)
            ip = entry.src_ip

            if ip in BLACKHOLE_ADDRESS: #ignore packet from backhole
                continue

            timestamp_date = datetime.fromtimestamp(timestamp)

            if windowS <= timestamp_date <= windowE:
                timestamp_window.append((timestamp, isn))

            if isn not in isn_dico:
                isn_dico[isn] = 1
            isn_dico[isn] += 1


    isn_dico_filtered = {}
    for isn, num in isn_dico.items():
        if num < THRESHOLD_IGNORE:
            continue
        else:
            isn_dico_filtered[isn] = num


    print('Sorting')
    timestamp_window.sort(key=lambda x: x[0])

    with open("make_stats_isn_overtime.output", "w") as f:
        f.write(str([timestamp_window, isn_dico_filtered]))

 
if __name__ == '__main__':
    compute_then_make_stat()
    #only_put_in_redis()

