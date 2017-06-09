#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

'''
#
'''

import sys
import argparse
import redis
import struct, socket
from datetime import datetime
import numpy as np
import csv
from pprint import pprint
sys.path.append('../../')
from put_in_redis import Entry
import ast
from statistics import mean, median, pstdev, pvariance



# CONFIG #
dataset = "blackhole27"
IPS_BLACKHOLE = 'xxx.xxx.xxx.xxx'

# REDIS #
serv_mirai = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=0)
serv_all = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=10)
serv_ip =  redis.StrictRedis(
    host='localhost',
    port=6501,
    db=5)


def make_stat():
    print("Computing Stats")

    all_dates = serv_mirai.keys(dataset+':20*')

    dico_ttl = {}
    iter_num = 0
    print("port 23/2323 and not icmp")
    for date in all_dates:
        print("progress: {}%".format(int(iter_num/len(all_dates)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        processed_ip_day = set()

        #dic = serv_mirai.smembers(ip.decode("utf-8"))
        for entry_json in serv_mirai.smembers(date):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
        
            #ignore blackhole response
            if IPS_BLACKHOLE in entry.src_ip:
                continue

            #ignore same ip day
            if entry.src_ip in processed_ip_day:
                continue
            else:
                processed_ip_day.add(entry.src_ip)

            ttl = int(entry.ttl)
            try:
                dico_ttl[ttl] += 1
            except KeyError:
                dico_ttl[ttl] = 1

    #fill ttl gap
    for i in range(0, 255):
        try:
            dico_ttl[i] += 0
        except:
            dico_ttl[i] = 0


    dico_ttl_all = {}
    iter_num = 0
    print("not icmp")
    for date in all_dates:
        print("progress: {}%".format(int(iter_num/len(all_dates)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        processed_ip_day = set()

        #dic = serv_mirai.smembers(ip.decode("utf-8"))
        for entry_json in serv_all.smembers(date):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
        
            #ignore blackhole response
            if IPS_BLACKHOLE in entry.src_ip:
                continue

            #ignore same ip day
            if entry.src_ip in processed_ip_day:
                continue
            else:
                processed_ip_day.add(entry.src_ip)

            ttl = int(entry.ttl)
            try:
                dico_ttl_all[ttl] += 1
            except KeyError:
                dico_ttl_all[ttl] = 1

    #fill ttl gap
    for i in range(0, 255):
        try:
            dico_ttl_all[i] += 0
        except:
            dico_ttl_all[i] = 0


    dico_ttl_session = {}
    iter_num = 0
    print('Only session')
    for date in all_dates:
        print("progress: {}%".format(int(iter_num/len(all_dates)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        processed_ip_day = set()

        #dic = serv_mirai.smembers(ip.decode("utf-8"))
        for entry_json in serv_all.smembers(date):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
        
            #ignore blackhole response
            if IPS_BLACKHOLE in entry.src_ip:
                continue

            #ignore same ip day
            if entry.src_ip in processed_ip_day:
                continue
            else:
                processed_ip_day.add(entry.src_ip)

            #check if IP has a telnet session
            if serv_ip.exists(entry.src_ip):
                #check if telnet session makes senses (commands send)
                dico_all_session_from_ip = serv_ip.hgetall(entry.src_ip)
                for timestamp, session in dico_all_session_from_ip.items():
                    if len(session) >= 3:
                        ttl = int(entry.ttl)
                        try:
                            dico_ttl_session[ttl] += 1
                        except KeyError:
                            dico_ttl_session[ttl] = 1
                        break

    #fill ttl gap
    for i in range(0, 255):
        try:
            dico_ttl_session[i] += 0
        except:
            dico_ttl_session[i] = 0



    with open("make_stats_ttl_repartition.output", 'w') as f:
        f.write(str([dico_ttl, dico_ttl_all, dico_ttl_session]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    args = parser.parse_args()
    
    make_stat()

