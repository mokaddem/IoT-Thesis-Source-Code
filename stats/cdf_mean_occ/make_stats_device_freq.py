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
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import csv
sys.path.append('../../')
from put_in_redis import Entry
from statistics import mean, median, pstdev, pvariance


# CONFIG #
dataset = "blackhole1"
ONE_DAY = 60*60*24 #1 day
ACCEPTATION_WINDOW = ONE_DAY*1 #1 day


# REDIS #
serv0 = redis.StrictRedis(
    host='localhost',
    port=6500,
    db=0)
serv1 = redis.StrictRedis(
    host='localhost',
    port=6500,
    db=1)

def put_data_in_redis():
    print("Putting in redis")
    
    #put_in_redis_per_ip
    all_keys = serv0.keys(dataset+":20"+"*")

    total_processed = 0
    
    for day_num, ip_day in enumerate(all_keys):
        format_date = ip_day.decode().split(":")[1]
        for entry_json in serv0.smembers(ip_day):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
            total_processed += 1

            if socket.inet_ntoa(struct.pack('!L', int(entry.isn))) == entry.dst_ip:
                to_save = [entry.src_port, entry.dst_ip, entry.dst_port, entry.isn, entry.flags, entry.ttl]
                serv1.hset(entry.src_ip, entry.timestamp, str(to_save))
                serv1.sadd("all_ips", entry.src_ip)

        print(day_num, len(all_keys))


#For an IP with isn=ip.dst, count how many times it appear within a windows
#Then, make an average of all these occurences
def make_stat():
    print("Computing Stats")

    #make_stat
    all_ips = serv1.smembers("all_ips")

    ips = {} #total number of occurence within the acceptation window per ip
    iter_num = 0
    for ip in all_ips:

        if(iter_num % int(len(all_ips)/100) == 0):
            print("progress: {}%".format(int(iter_num/len(all_ips)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        ip_timestamps = serv1.hkeys(ip)
        ip_timestamps.sort()

        i = 0
        while i < len(ip_timestamps):
            count = 0
            flag_break = False
            for j in range(i+1, len(ip_timestamps)):
                if float(ip_timestamps[j]) - float(ip_timestamps[i]) < ACCEPTATION_WINDOW:
                    count += 1
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
    with open("make_stats_freq_ip_cdf.output", "w") as f:
        f.write(str([list(X), list(Y), dico_stat]))

    #plot
    the_plot = plt.plot(X, Y)
    plt.title("CDF of the mean(occurences IP.src) within the acceptation window ("+str(int(ACCEPTATION_WINDOW/ONE_DAY))+" day) per unique ip")
    plt.ylabel("CDF")
    plt.xlabel("Occurence")
    plt.xscale('log')
    plt.show()


  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    parser.add_argument('-r', '--refresh', required=False, default=False, help='Refresh the data in redis')
    args = parser.parse_args()
    
    if args.refresh == True:
        put_data_in_redis()
    else:
        make_stat()

