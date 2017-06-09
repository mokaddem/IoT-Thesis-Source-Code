#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

'''
This program extract telnet data from a cap file into redis (set datastructure).
    - dataset:timestamp     -----set----->  Entry
    - dataset:ip            --timestamp-->  telnetData    
'''

import redis
import json
import time
import argparse
import datetime
import os
import re
from subprocess import PIPE, Popen

# CONFIG #
BLACKHOLE_ADDRESS = "xxx.xxx.xxx.xxx"
tshark_command_get_info_JSON = 'tshark -n -z "follow,tcp,raw,{tcpFlowNum}" -r {pcapName}\
 -T json -e frame.time_epoch\
 -T json -e ip.src\
 -T json -e tcp.srcport\
 -T json -e ip.dst\
 -T json -e tcp.dstport\
 -T json -e tcp.seq\
 -T json -e tcp.flags\
 -T json -e ip.ttl\
 -T json -e telnet.cmd\
 -T json -e telnet.subcmd\
 -T json -e telnet.data\
 -T json -e ip.geoip.src_asnum\
 -T json -e ip.geoip.src_country\
 -o tcp.relative_sequence_numbers:FALSE\
 "not icmp and tcp.stream eq {tcpFlowNum}" and not tcp.analysis.spurious_retransmission'
 #"not icmp and tcp.stream eq {tcpFlowNum}" '

command_get_all_stream = 'tshark -n -z "follow,tcp,raw,1" -r {pcapName} -T fields -e tcp.stream "telnet"'

### Entry class ###
class Entry():
    def __init__(self, src_ip, src_port, dst_ip, dst_port, isn, flags, ttl, timestamp, telnetData, asn, country):
        self.timestamp = timestamp
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.isn = isn.split(",")[0]
        self.flags = flags
        self.ttl = ttl
        self.asn = asn
        self.country = country
        self.telnetData = telnetData
        self.flag_carriage_added = False

    def jsonify(self):
        #remove flag
        dico = self.__dict__
        dico.pop('flag_carriage_added', None)
        temp = json.dumps(dico, default=lambda o: o.__dict__)
        return temp

    def create_entry_from_redis(redis_response):
        temp = json.loads(redis_response)
        return Entry(temp['src_ip'], 
                temp['src_port'], 
                temp['dst_ip'], 
                temp['dst_port'], 
                temp['isn'], 
                temp['flags'], 
                temp['ttl'],
                temp['timestamp'],
                temp['telnetData'])

    def addTelnetData(self, data):
        if len(data) == 0:
            return
        if len(data) == 1 and data[0] == '':
            return

        for d in data:
            self.telnetData.append(d)
        

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

def filter_stream_num(stream):
    all_stream = stream.read().decode('utf8')
    all_stream = all_stream.split("===================================================================")[0]
    streams = []
    for s in all_stream.splitlines():
        if s not in streams and s != '':
            streams.append(s)
    return streams


### Program ###
def main(args, basename, key_setAndFile, serv_ip, serv_session):
    if checkFormat():
        
        #Get all the tcp stream
        p_stream = Popen([command_get_all_stream.format(pcapName=args.sourcefile)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 
        all_stream_num = filter_stream_num(p_stream.stdout)
        for stream_num in all_stream_num:
            stream_num = stream_num
            #filter out non-digit
            if not stream_num.isdigit():
                continue

            #Get the telnet session data
            p_data = Popen([tshark_command_get_info_JSON.format(pcapName=args.sourcefile, tcpFlowNum=stream_num)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 

            lineNumber = 0
            ip1 = None
            ip2 = None
            dic = {}
            prev_added_ip = None
            telnet_session_echo = None

            allLines = p_data.stdout.read()
            allLines = allLines.decode("utf-8")
            session_array = allLines.split("===================================================================")
            session_array_filtered = []
            #Filter out stats related to sessions generated by tshark
            for i, elem in enumerate(session_array):
                if i % 2 == 0:
                    session_array_filtered += [elem]

            #parse tshark output to generate a session array composed of packets
            complete_session = []
            for session_string in session_array_filtered:
                if session_string == "\n":
                    continue
                try:
                    session = json.loads(session_string)
                except json.decoder.JSONDecodeError:
                    print(session_string, args.sourcefile, stream_num)
                    continue
                complete_session += session

            lineNumber = 0
            for packet in complete_session:
                infos = packet['_source']['layers']
                timestamp = infos['frame.time_epoch'][0]
                ipSrc = infos['ip.src'][0]
                tcpSrc = infos['tcp.srcport'][0]
                ipDst = infos['ip.dst'][0]
                tcpDst = infos['tcp.dstport'][0]
                seq = infos['tcp.seq'][0]
                flags = infos['tcp.flags'][0]
                ttl = infos['ip.ttl'][0]

                #geoip
                try:
                    asn = infos['ip.geoip.src_asnum'][0]
                except KeyError:
                    asn = ""
                try:
                    country = infos['ip.geoip.src_country'][0]
                except KeyError:
                    country = ""

                #telnet
                try:
                    telnetCmd = infos['telnet.cmd']
                except KeyError:
                    telnetCmd = ""
                try:
                    telnetSubcmd = infos['telnet.subcmd']
                except KeyError:
                    telnetSubcmd = ""
                try:
                    telnetData = infos['telnet.data']
                except KeyError:
                    telnetData = []

                #create object by IP then, update it during the session
                if lineNumber == 0:
                    ip1 = ipSrc
                    dic[ip1] = Entry(ipSrc, [tcpSrc], ipDst, tcpDst, seq, flags, ttl, timestamp, telnetData, asn, country)
                elif (ip2 is None) and (ipSrc != ip1):
                    ip2 = ipSrc
                    dic[ip2] = Entry(ipSrc, [tcpSrc], ipDst, tcpDst, seq, flags, ttl, timestamp, telnetData, asn, country)
                else:
                    dic[ipSrc].addTelnetData(telnetData)
                    #add src port
                    if tcpSrc not in dic[ipSrc].src_port:
                        dic[ipSrc].src_port.append(tcpSrc)
                    #add geoIP info
                    if dic[ipSrc].asn == "":
                        dic[ipSrc].asn = asn
                    if dic[ipSrc].country == "":
                        dic[ipSrc].country = country

                prev_added_ip = ipSrc

                #check if remote requested echo
                for cmd, val in zip(telnetCmd, telnetSubcmd):
                    if cmd == '':
                        continue
                    #253=DO, 1=ECHO
                    if int(cmd) == 253 and int(val) == 1 and (BLACKHOLE_ADDRESS not in ipSrc):
                        telnet_session_echo = True

                lineNumber += 1

            '''Add into redis only remote IP (ignoring blackhole)'''
            if ip1 is None or ip2 is None:
                continue
            remote_ip = ip1 if (BLACKHOLE_ADDRESS not in ip1) else ip2
            blackhole_ip = ip2 if (BLACKHOLE_ADDRESS not in ip1) else ip1
            infos = dic[remote_ip]
            infos_blackhole = dic[blackhole_ip]

            # dataset:ip    --timestamp-->  telnetData    
            red_hash = args.dataset+':'+remote_ip
            key = infos.timestamp
            serv_ip.hset(remote_ip, key, infos.telnetData)
            #print(remote_ip,"-->", key (timestamp),"-->", infos.telnetData)

            the_date = infos.timestamp
            session_toSave = ""
            blackhole_session_toSave = ""
            for key, elem in dic.items():
                if elem.src_ip == remote_ip:
                    session_toSave += "".join(elem.telnetData)
                else:
                    blackhole_session_toSave += "".join(elem.telnetData)
                
            dico_session_toSave = {'session_remote': session_toSave, 'session_blackhole': blackhole_session_toSave, 'ip_remote': remote_ip, 'ip_blackhole': blackhole_ip, 'echo': telnet_session_echo, 'src_port': infos.src_port, 'asn': infos.asn, 'country': infos.country}
            serv_session.sadd(the_date, dico_session_toSave)
            #print(the_date, '-->', str(dico_session_toSave))
            
            
            '''Keep track of the successfully processed file'''

if __name__ == '__main__':
    # REDIS #
    serv_ip = redis.StrictRedis(
        host='localhost',
        port=6501,
        db=5)
    serv_session = redis.StrictRedis(
        host='localhost',
        port=6501,
        db=6)
    
    parser = argparse.ArgumentParser(description='Import data from a cap file into redis.')
    parser.add_argument('-s', '--sourcefile', required=True, help='The source file to be imported')
    parser.add_argument('-d', '--dataset', required=True, help='Which dataset the file comes from')
    parser.add_argument('-f', '--format', required=False, default='ymdhM', help='Which key format will be used in redis, \ny = year, m = month, d = day, h = hour and M = minute.')
    args = parser.parse_args()
    basename = os.path.basename(args.sourcefile).split('.')[0]
    
    key_setAndFile = args.dataset + ':' + basename

    main(args, basename, key_setAndFile, serv_ip, serv_session)

