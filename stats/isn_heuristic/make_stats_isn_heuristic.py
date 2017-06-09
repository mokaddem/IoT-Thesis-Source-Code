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

# REDIS #
serv_all = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=10)
serv_ip_matching_isn = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=7)
def only_put_in_redis():

    all_dates = serv_all.keys(dataset+":20"+"*")
    isn_matching_non_telnet = set()

    iter_num = 0
    for ip_day in all_dates:
        print("progress: {}%".format(int(iter_num/len(all_dates)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        for entry_json in serv_all.smembers(ip_day):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))

            if socket.inet_ntoa(struct.pack('!L', int(entry.isn))) == entry.dst_ip:

                if int(entry.dst_port) == 23 or int(entry.dst_port) == 2323:
                    serv_ip_matching_isn.sadd(entry.src_ip, entry.timestamp)
                else:
                    isn_matching_non_telnet.add((entry.src_ip, entry.timestamp))

    with open('isn_matching_non_telnet.txt', 'w') as f:
        f.write(str(isn_matching_non_telnet))

def compute_then_make_stat():
    
    all_keys = serv_all.keys(dataset+":20"+"*")

    compromised_entry = set()
    compromised_ip = set()
    processed_ip = set()
    total_uniq_processed = 0
    
    graph_23 = {}
    graph_2323 = {}
    graph_sum = {}
    graph_tot_sum = {}

    for day_num, ip_day in enumerate(all_keys):
        format_date = ip_day.decode().split(":")[1]
        processed_ip_day = set()
        compromised_ip_today = set()
        for entry_json in serv_all.smembers(ip_day):
            entry = Entry.create_entry_from_redis(entry_json.decode("utf-8"))
            if entry.src_ip not in processed_ip:
                total_uniq_processed += 1
                processed_ip.add(entry.src_ip)

            if entry.src_ip not in processed_ip_day:
                processed_ip_day.add(entry.src_ip)
                try:
                    graph_tot_sum[format_date] += 1
                except:
                    graph_tot_sum[format_date] = 1

            if socket.inet_ntoa(struct.pack('!L', int(entry.isn))) == entry.dst_ip:
                compromised_ip.add(entry.src_ip)
                compromised_entry.add(entry)

                if int(entry.dst_port) == 23:
                    try:
                        if entry.src_ip in compromised_ip_today:
                            continue
                        graph_23[format_date] += 1
                        graph_sum[format_date] += 1
                    except:
                        graph_23[format_date] = 1
                        graph_sum[format_date] = 1
                elif int(entry.dst_port) == 2323:
                    try:
                        if entry.src_ip in compromised_ip_today:
                            continue
                        graph_2323[format_date] += 1
                        graph_sum[format_date] += 1
                    except:
                        graph_2323[format_date] = 1
                        graph_sum[format_date] = 1
                else:
                    pass

                compromised_ip_today.add(entry.src_ip)
        print(day_num, len(all_keys))

    #print(len(compromised_ip))
    #print(len(compromised_entry))
    #print(total_uniq_processed)
    #print(graph)

    date_23 = []
    value_23 = []
    date_2323 = []
    value_2323 = []
    date_sum = []
    value_sum = []
    date_tot_sum = []
    value_tot_sum = []

    all_data_23 = []
    all_data_2323 = []
    all_data_sum = []
    all_data_tot_sum = []
    for k, v in graph_23.items():
        all_data_23.append([k,v])
    all_data_23.sort(key=lambda x: int(x[0]))
    for k, v in graph_2323.items():
        all_data_2323.append([k,v])
    all_data_2323.sort(key=lambda x: int(x[0]))
    for k, v in graph_sum.items():
        all_data_sum.append([k,v])
    all_data_sum.sort(key=lambda x: int(x[0]))
    for k, v in graph_tot_sum.items():
        all_data_tot_sum.append([k,v])
    all_data_tot_sum.sort(key=lambda x: int(x[0]))


    for elem in all_data_23:
        y = int(elem[0][0:4])
        m = int(elem[0][4:6])
        d = int(elem[0][6:8])
        date_23.append( datetime(y, m, d) )
        value_23.append(int(elem[1]))
    for elem in all_data_2323:
        y = int(elem[0][0:4])
        m = int(elem[0][4:6])
        d = int(elem[0][6:8])
        date_2323.append( datetime(y, m, d) )
        value_2323.append(int(elem[1]))
    for elem in all_data_sum:
        y = int(elem[0][0:4])
        m = int(elem[0][4:6])
        d = int(elem[0][6:8])
        date_sum.append( datetime(y, m, d) )
        value_sum.append(int(elem[1]))
    for elem in all_data_tot_sum:
        y = int(elem[0][0:4])
        m = int(elem[0][4:6])
        d = int(elem[0][6:8])
        date_tot_sum.append( datetime(y, m, d) )
        value_tot_sum.append(int(elem[1]))




    with open("make_stats23_2323_sum.output", "w") as f:
        f.write(str([all_data_23, all_data_2323, all_data_sum, all_data_tot_sum, total_uniq_processed]))

 
if __name__ == '__main__':
    #compute_then_make_stat()
    only_put_in_redis()

