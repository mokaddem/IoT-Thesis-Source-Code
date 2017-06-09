#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

'''
This program import data from a cap file into redis (set datastructure).

###Actual data:                                            dataset:filename:dateFormat             -> data
Actual data:                                            dataset:dateFormat                 -> data

Successfull processed files are recorded under the key: dataset:"Success_sourcefile"    -> filename
Files with error in line(s) are recorded under the key: dataset:"Failed_sourcefile"     -> filename
Line with an error are recorded under the key:          dataset:filename:"Failed_line"  -> line_number

'''

import redis
import json
import time
import argparse
import datetime
from pprint import pprint
import ast
import json
import os
from subprocess import PIPE, Popen

# CONFIG #
REDIS_PORT = 6501
REDIS_DB = 11

tshark_command = 'tshark -n -r {}\
 -T json -e frame.time_epoch\
 -T json -e ip.src\
 -T json -e tcp.srcport\
 -T json -e ip.dst\
 -T json -e tcp.dstport\
 -T json -e tcp.seq\
 -T json -e tcp.flags\
 -T json -e ip.ttl\
 -o tcp.relative_sequence_numbers:FALSE \"tcp.port==2323 or tcp.port==23 and not icmp\"' #filter out icmp packets
 #-o tcp.relative_sequence_numbers:FALSE \"not icmp\"' #filter out icmp packets
 #-o tcp.relative_sequence_numbers:FALSE \"tcp.port==2323 or tcp.port==23\"'

### Entry class ###
class Entry():
    def __init__(self, src_ip, src_port, dst_ip, dst_port, isn, flags, ttl, timestamp):
        self.timestamp = timestamp
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.isn = isn.split(",")[0]
        self.flags = flags
        self.ttl = ttl

    def jsonify(self):
        temp = json.dumps(self, default=lambda o: o.__dict__)
        return temp

    def create_entry_from_redis(redis_response):
        #temp = json.loads(redis_response.decode('utf-8'))
        temp = json.loads(redis_response)
        return Entry(temp['src_ip'], 
                temp['src_port'], 
                temp['dst_ip'], 
                temp['dst_port'], 
                temp['isn'], 
                temp['flags'], 
                temp['ttl'],
                temp['timestamp'])

    def __repr__(self):
        return str(self.__dict__)


### Functions definition ###
'''
return the IP key with the form:
    dataset_name:sourcefile_name:specified_format
Example: with format ymdh, a key could be dataset_name:sourcefile_name:2016161118
'''
def getIpKeyFromTimestamp(timestamp):
        return key_setAndFile + ':' + getFormatFromTimestamp(timestamp)

def getFormatFromTimestamp(timestamp):
    thedatetime = datetime.datetime.fromtimestamp(float(timestamp))
    year = thedatetime.year
    month = thedatetime.month
    day = thedatetime.day
    hour = thedatetime.hour
    minute = thedatetime.minute

    key = ""
    for l in args.format:
        if l == 'y':
            key += str(year)
        elif l == 'm':
            key += str(month).zfill(2)
        elif l == 'd':
            key += str(day).zfill(2)
        elif l == 'h':
            key += str(hour).zfill(2)
        elif l == 'M':
            key += str(minute).zfill(2)
        else:
            print('unknow format')
    return key



def checkFormat():
    for l in args.format:
        if l != 'y' and l != 'm' and l != 'd' and l != 'h' and l != 'M':
            print('unknow format!')
            return False
    return True


### Program ###
def main(args, basename, key_setAndFile, serv):
    if checkFormat():
        
        #Check if source file from this dataset has already been processed -> Keep it if it becomes useful
        if not serv.sismember(args.dataset+":Failed_sourcefile", basename) or args.overwrite == 1:
        
            lineNumber = 0
            p = Popen([tshark_command.format(args.sourcefile)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 
            data = p.stdout.read()
            data = data.decode("utf-8")

            try:
                data = json.loads(data)
            except json.decoder.JSONDecodeError:
                print(packet, args.sourcefile)

            for packet in data:
                try:
                    packet = packet['_source']['layers']
                    timestamp = packet['frame.time_epoch'][0]
                    ipSrc = packet['ip.src'][0]
                    tcpSrc = packet['tcp.srcport'][0]
                    ipDst = packet['ip.dst'][0]
                    tcpDst = packet['tcp.dstport'][0]
                    seq = packet['tcp.seq'][0]
                    flags = packet['tcp.flags'][0]
                    ttl = packet['ip.ttl'][0]


                    ipKey = getIpKeyFromTimestamp(timestamp)
                    the_date = args.dataset + ":" + getFormatFromTimestamp(timestamp) 
            
                    #Add into redis
                    infos =  Entry(ipSrc, tcpSrc, ipDst, tcpDst, seq, flags, ttl, timestamp)
                    to_save = infos.jsonify()

                    #serv.sadd(ipKey, to_save)
                    #serv.sadd(the_date, to_save)
                    serv.sadd(ipSrc, to_save)
            
                    #Keep track of the successfully processed line
                    #serv.sadd(key_setAndFile, lineNumber)

                    lineNumber+=1

                except KeyError as e:
                    pass
            
                except Exception as e:
                    print(str(e)+" - ", packet, args.sourcefile)
                    #Add the failed line in redis
                    serv.sadd(key_setAndFile+":Failed_line", lineNumber)
                    #Add the file which contain an error in redis
                    serv.sadd(args.dataset+":Failed_sourcefile", basename)
                    continue
            
            #Keep track of the successfully processed file
            #serv.sadd(args.dataset+":Success_sourcefile", basename)


if __name__ == '__main__':
    # REDIS #
    serv = redis.StrictRedis(
        host='localhost',
        port=REDIS_PORT,
        db=REDIS_DB)
    
    
    parser = argparse.ArgumentParser(description='Import data from a cap file into redis.')
    parser.add_argument('-s', '--sourcefile', required=True, help='The source file to be imported')
    parser.add_argument('-d', '--dataset', required=True, help='Which dataset the file comes from')
    parser.add_argument('-f', '--format', required=False, default='ymd', help='Which key format will be used in redis, \ny = year, m = month, d = day, h = hour and M = minute.')
    parser.add_argument('-o', '--overwrite', type=int, required=False, default='0', help='') #Keep it in case it becomes useful
    args = parser.parse_args()
    basename = os.path.basename(args.sourcefile).split('.')[0]
    
    key_setAndFile = args.dataset + ':' + basename

    main(args, basename, key_setAndFile, serv)

