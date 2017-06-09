#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

'''
#   Takes all the records in the db0 consisting of   dataset:date_format -> entry
#   then put inside db1 the record                  ip                  -> (timestamp -> list(entry))
#
#   Second part process this added data to deduce the device frequency with an acceptation window
#
'''

import sys
import argparse
import redis
import struct, socket
from datetime import datetime
import numpy as np
import csv
import ast
import pprint
from statistics import mean, median, pstdev, pvariance




# CONFIG #
dataset = "blackhole1"
ONE_DAY = 60*60*24 #1 day
ACCEPTATION_WINDOW = ONE_DAY*1 #1 day


# REDIS #
serv_ip = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=5)
serv_timestamp = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=6)

to_further_process = []

''' A session is considered valid if there are at least 2 msgs sent (typically, credential)'''
def is_valid_telnet_session(ip, timestamp):
    global to_further_process
    for session in serv_timestamp.smembers(timestamp):
        session = ast.literal_eval(session.decode('utf-8'))
        ip_remote = session['ip_remote']
        session_remote = session['session_remote']
    
        if ip_remote != ip.decode('utf8'):
            to_further_process += [(ip, timestamp)]
        else:
            array_remote = session_remote.split('\n')
            if len(array_remote) < 2:
                return False
            else:
                return True

def make_stat():
    print("Computing Stats")

    #make_stat
    all_ips = serv_ip.keys('*')

    ips = {} #total number of occurence within the acceptation window per ip
    iter_num = 0
    for ip in all_ips:

        if(iter_num % int(len(all_ips)/100) == 0):
            print("progress: {}%".format(int(iter_num/len(all_ips)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        ip_timestamps = serv_ip.hkeys(ip)
        ip_timestamps.sort()

        i = 0
        while i < len(ip_timestamps):
            count = 1
            flag_break = False
            for j in range(i+1, len(ip_timestamps)):
                if float(ip_timestamps[j]) - float(ip_timestamps[i]) < ACCEPTATION_WINDOW:
                    if is_valid_telnet_session(ip, ip_timestamps[j]):
                        count += 1
                    else:
                        pass
                else:
                    i = j
                    flag_break = True
                    break
            try:
                ips[ip].append(count) 
            except:
                ips[ip] = [count]
            i = len(ip_timestamps) if not flag_break else i

    tab_occ = []
    for ip, occ in ips.items():
        tab_occ += [int(mean(occ))]

    dico_stat = {}
    dico_stat["mean"] = mean(tab_occ)
    dico_stat["median"] = median(tab_occ)
    dico_stat["std_dev"] = pstdev(tab_occ)
    dico_stat["variance"] = pvariance(tab_occ)
    dico_stat["max"] = max(tab_occ)
    pprint.pprint(to_further_process)
    print("mean:", dico_stat["mean"])
    print("median:", dico_stat["median"])
    print("standard deviation:", dico_stat["std_dev"])
    print("variance:", dico_stat["variance"])
    print("max:", dico_stat["max"])

    occ_ip = np.array(list(tab_occ))
    occ_sorted = np.sort(occ_ip)

    N = len(occ_sorted)
    dico_stat["n"] = N
    X = np.sort(occ_sorted)
    Y = np.array(range(N))/float(N)

    #save on disk
    with open("make_stats_telnet_cdf_ip_login.output", "w") as f:
        f.write(str([list(X), list(Y), dico_stat]))

    ##plot

  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    args = parser.parse_args()

    make_stat()

