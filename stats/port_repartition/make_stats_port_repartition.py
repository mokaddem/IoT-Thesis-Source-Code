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
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import csv
sys.path.append('../../')
from put_in_redis import Entry
import ast
from statistics import mean, median, pstdev, pvariance



# CONFIG #
dataset = "blackhole1"

# REDIS #
serv0 = redis.StrictRedis(
    host='localhost',
    port=6500,
    db=0)
serv1 = redis.StrictRedis(
    host='localhost',
    port=6500,
    db=1)

def plot_data():
    return

def make_stat():
    print("Computing Stats")

    all_ips = serv1.smembers("all_ips")

    dico_srcport = {}
    dico_dstport = {}
    iter_num = 0
    for ip in all_ips:
        if(iter_num % int(len(all_ips)/100) == 0):
            print("progress: {}%".format(int(iter_num/len(all_ips)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        dic = serv1.hgetall(ip.decode("utf-8"))
        for timestamp, array in dic.items():
            tab = ast.literal_eval(array.decode("utf-8"))
            src_port = tab[0]
            dst_ip = tab[1]
            dst_port = tab[2]
            isn = tab[3]
            flags = tab[4]
            ttl = tab[5]

            try:
                dico_srcport[int(src_port)] += 1
                dico_dstport[int(dst_port)] += 1
            except:
                dico_srcport[int(src_port)] = 1
                dico_dstport[int(src_port)] = 1

    #fill port gap
    for i in range(0, max(dico_srcport)):
        try:
            dico_srcport[i] += 0
        except:
            dico_srcport[i] = 0
    for i in range(0, max(dico_dstport)):
        try:
            dico_dstport[i] += 0
        except:
            dico_dstport[i] = 0


    with open("make_stats_port_repartition.output", 'w') as f:
        f.write(str([dico_srcport, dico_dstport]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    parser.add_argument('-plot', '--plot', required=False, default=False, help='plot the data')
    args = parser.parse_args()
    
    if args.plot == True:
        plot_data()
    else:
        make_stat()

