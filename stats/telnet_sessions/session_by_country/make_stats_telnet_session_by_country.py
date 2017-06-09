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
import json
from pprint import pprint
from statistics import mean, median, pstdev, pvariance


# CONFIG #
dataset = "blackhole27"
fetch_commands = ['tftp', 'wget', 'curl', 'nc']


# REDIS #
serv_ip = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=5)
serv_timestamp = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=6)


def make_stat():
    print("Computing Stats")

    #make_stat
    all_timestamp = serv_timestamp.keys('*.*')

    dico_country = {} #total number of occurence within the acceptation window per ip
    dico_country_uniq_ip = {} #total number of occurence within the acceptation window per ip
    tot_sum = 0
    dico_country_distri = {} #total number of occurence within the acceptation window per ip
    dico_country_distri_uniq_ip = {}
    tot_sum_distri = 0
    iter_num = 0
    for timestamp in all_timestamp:

        if(iter_num % int(len(all_timestamp)/100) == 0):
            print("progress: {}%".format(int(iter_num/len(all_timestamp)*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        for session in serv_timestamp.smembers(timestamp):
            session = ast.literal_eval(session.decode('utf-8'))
            telnet_session = session['session_remote']
            ip = session['ip_remote'] 
            country = session['country']
            if country not in dico_country:
                dico_country[country] = 0
                dico_country_uniq_ip[country] = set()
            dico_country_uniq_ip[country].add(ip)
            dico_country[country] += 1
            tot_sum += 1

            #if distri - AGGRESSIVE CHECK!!
            #check if fetch command
            for cmd in fetch_commands:
                if cmd in telnet_session:
                    if country not in dico_country_distri:
                        dico_country_distri[country] = 0
                        dico_country_distri_uniq_ip[country] = set()
                    dico_country_distri[country] += 1
                    dico_country_distri_uniq_ip[country].add(ip)
                    tot_sum_distri += 1


    ##ALL
    dico_country_perc = {}
    list_country_perc = []
    list_country = []
    for country, val in dico_country.items():
        perc = val / tot_sum
        dico_country_perc[country] = perc
        list_country_perc.append((country, perc))
        list_country.append((country, val))

    list_country_perc.sort(key=lambda x: x[1], reverse=True)
    list_country.sort(key=lambda x: x[1], reverse=True)

    #sort uniq ip
    list_country_uniq_ip = []
    for country, val in list_country:
        list_country_uniq_ip.append((country, len(dico_country_uniq_ip[country])))

    ##DISTRI
    import math
    dico_country_distri_perc = {}
    list_country_distri_perc = []
    list_country_distri = []
    list_country_distri_log = []
    for country, val in dico_country_distri.items():
        perc = val / tot_sum_distri
        dico_country_distri_perc[country] = perc
        list_country_distri_perc.append((country, perc))
        list_country_distri.append((country, val))
        list_country_distri_log.append((country, math.log(val)))

    list_country_distri_perc.sort(key=lambda x: x[1], reverse=True)
    list_country_distri.sort(key=lambda x: x[1], reverse=True)
    list_country_distri_log.sort(key=lambda x: x[1], reverse=True)

    #sort uniq ip
    list_country_distri_uniq_ip = []
    for country, val in list_country_distri:
        list_country_distri_uniq_ip.append((country, len(dico_country_distri_uniq_ip[country])))

    #pprint(list_country_perc)
    #pprint(list_country)

    #save on disk
    with open("make_stats_telnet_country.output", "w") as f:
        json.dump([[list_country, list_country_perc, list_country_uniq_ip], [list_country_distri, list_country_distri_perc, list_country_distri_log, list_country_distri_uniq_ip]], f)

  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the country of IP having a telnet session')
    args = parser.parse_args()

    make_stat()

