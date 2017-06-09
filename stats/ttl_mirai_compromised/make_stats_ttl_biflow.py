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
ONE_DAY = 60*60*24
ONE_HOUR = 60*60

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
    print("Collecting data")

    all_dates = serv_all.keys(dataset+':20*')

    dico_ip_to_ttl_23 = {}
    dico_delta_ttl_23_10s = {}
    dico_delta_ttl_23_6h = {}
    dico_delta_ttl_23_24h = {}
    
    dico_ip_to_ttl_2323 = {}
    dico_delta_ttl_2323_10s = {}
    dico_delta_ttl_2323_6h = {}
    dico_delta_ttl_2323_24h = {}

    dico_ip_to_ttl_session = {}
    dico_delta_ttl_session_10s = {}
    dico_delta_ttl_session_6h = {}
    dico_delta_ttl_session_24h = {}
    
    # fill dico
    for x in range(0, 255):
        dico_delta_ttl_23_6h[x] = 0
        dico_delta_ttl_23_10s[x] = 0
        dico_delta_ttl_23_24h[x] = 0

        dico_delta_ttl_2323_6h[x] = 0
        dico_delta_ttl_2323_10s[x] = 0
        dico_delta_ttl_2323_24h[x] = 0

        dico_delta_ttl_session_6h[x] = 0
        dico_delta_ttl_session_10s[x] = 0
        dico_delta_ttl_session_24h[x] = 0

    iter_num = 0
    for date in all_dates:
        print("progress: {}%".format(int(iter_num/len(all_dates)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        for entry_json in serv_mirai.smembers(date):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
            ttl = int(entry.ttl)
            timestamp = float(entry.timestamp)
        
            #ignore blackhole response
            if IPS_BLACKHOLE in entry.src_ip:
                continue

            #consider port 23
            if int(entry.dst_port) == 23:
                if entry.src_ip not in dico_ip_to_ttl_23:
                    dico_ip_to_ttl_23[entry.src_ip] = [(timestamp, ttl)]
                else:
                    dico_ip_to_ttl_23[entry.src_ip].append((timestamp, ttl))
            #consider port 2323
            elif int(entry.dst_port) == 2323:
                if entry.src_ip not in dico_ip_to_ttl_2323:
                    dico_ip_to_ttl_2323[entry.src_ip] = [(timestamp, ttl)]
                else:
                    dico_ip_to_ttl_2323[entry.src_ip].append((timestamp, ttl))
            #consider logged telnet session
            if serv_ip.exists(entry.src_ip):
                #check if telnet session makes senses (commands send)
                dico_all_session_from_ip = serv_ip.hgetall(entry.src_ip)
                for useless_timestamp, session in dico_all_session_from_ip.items():
                    if len(session) >= 3:
                        if entry.src_ip not in dico_ip_to_ttl_session:
                            dico_ip_to_ttl_session[entry.src_ip] = [(timestamp, ttl)]
                        else:
                            dico_ip_to_ttl_session[entry.src_ip].append((timestamp, ttl))
                        break

    print('Computing delta port 23')
    ips_big_delta_23 = {}
    tot_num_23 = 0
    for ip, array in dico_ip_to_ttl_23.items():
        array.sort(key=lambda x: x[0])
        tot_num_23 += len(array)

        #compute the delta
        for i in range(len(array)-1):
            d0 = array[i][0]
            d1 = array[i+1][0]
            delta_t = d1 - d0
            ttl0 = array[i][1]
            ttl1 = array[i+1][1]
            delta_ttl = abs(ttl0 - ttl1)

            # delta_t <= 10s
            if delta_t <= 10:
                dico_delta_ttl_23_10s[delta_ttl] += 1
            # delta_t <= 6h
            if delta_t <= ONE_HOUR*6:
                dico_delta_ttl_23_6h[delta_ttl] += 1
            # delta_t <= 24h
            if delta_t <= ONE_HOUR*24:
                dico_delta_ttl_23_24h[delta_ttl] += 1
                if delta_ttl > 30:
                    if ip not in ips_big_delta_23:
                        ips_big_delta_23[ip] = [(d0, d1)]
                    else:
                        ips_big_delta_23[ip].append([(d0, d1)])

    print('Computing delta port 2323')
    ips_big_delta_2323 = {}
    tot_num_2323 = 0
    for ip, array in dico_ip_to_ttl_2323.items():
        array.sort(key=lambda x: x[0])
        tot_num_2323 += len(array)

        #compute the delta
        for i in range(len(array)-1):
            d0 = array[i][0]
            d1 = array[i+1][0]
            delta_t = d1 - d0
            ttl0 = array[i][1]
            ttl1 = array[i+1][1]
            delta_ttl = abs(ttl0 - ttl1)

            # delta_t <= 10s
            if delta_t <= 10:
                dico_delta_ttl_2323_10s[delta_ttl] += 1
            # delta_t <= 6h
            if delta_t <= ONE_HOUR*6:
                dico_delta_ttl_2323_6h[delta_ttl] += 1
            # delta_t <= 24h
            if delta_t <= ONE_HOUR*24:
                dico_delta_ttl_2323_24h[delta_ttl] += 1
                if delta_ttl > 30:
                    if ip not in ips_big_delta_2323:
                        ips_big_delta_2323[ip] = [(d0, d1)]
                    else:
                        ips_big_delta_2323[ip].append([(d0, d1)])

    print('Computing delta for session')
    ips_big_delta_session = {}
    tot_num_session = 0
    for ip, array in dico_ip_to_ttl_session.items():
        array.sort(key=lambda x: x[0])
        tot_num_session += len(array)

        #compute the delta
        for i in range(len(array)-1):
            d0 = array[i][0]
            d1 = array[i+1][0]
            delta_t = d1 - d0
            ttl0 = array[i][1]
            ttl1 = array[i+1][1]
            delta_ttl = abs(ttl0 - ttl1)

            # delta_t <= 10s
            if delta_t <= 10:
                dico_delta_ttl_session_10s[delta_ttl] += 1
            # delta_t <= 6h
            if delta_t <= ONE_HOUR*6:
                dico_delta_ttl_session_6h[delta_ttl] += 1
            # delta_t <= 24h
            if delta_t <= ONE_HOUR*24:
                dico_delta_ttl_session_24h[delta_ttl] += 1
                if delta_ttl > 30:
                    if ip not in ips_big_delta_session:
                        ips_big_delta_session[ip] = [(d0, d1)]
                    else:
                        ips_big_delta_session[ip].append([(d0, d1)])



    print(len(ips_big_delta_23), len(ips_big_delta_2323), len(ips_big_delta_session))
    with open("make_stats_ttl_biflow.output", 'w') as f:
        port23 = [dico_delta_ttl_23_6h, dico_delta_ttl_23_24h, dico_delta_ttl_23_10s, tot_num_23]
        port2323 = [dico_delta_ttl_2323_6h, dico_delta_ttl_2323_24h, dico_delta_ttl_2323_10s, tot_num_2323]
        onlySession = [dico_delta_ttl_session_6h, dico_delta_ttl_session_24h, dico_delta_ttl_session_10s, tot_num_session]
        f.write(str([port23, port2323, onlySession]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    args = parser.parse_args()
    
    make_stat()

