#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

import requests
import sys,os
from datetime import datetime
from time import time
import argparse
import redis
import hashlib
import logging
import csv
import ast
import re
from subprocess import PIPE, Popen, check_call, CalledProcessError

import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

all_exec_cmd = set()

REDIS_PORT = 6500
REDIS_DB = 1

MAX_SOURCE_DOWNLOAD = 100
MAX_SOURCE_DOWNLOAD_PER_DAY = 10
TIMEOUT = 1 #sec

tftp_command = "/bin/busybox tftp -l {fnl} -r {fnr} -g {addr}"
wget_command = "wget -T "+str(TIMEOUT)+" -t 1 {addr}"
curl_command = "curl --max-time "+str(TIMEOUT)+" {addr}"
nc_command = "nc -w "+ str(TIMEOUT) +" {addr} > {fn}"

regex_ip = "(\d{1,3}\.)(\d{1,3}\.)(\d{1,3}\.)(\d{1,3}) (\d{1,4})"
reg_ip = re.compile(regex_ip)

'''
Stored in redis:

    - hash      ->  (url_name, timestamp, request_timestamp, status_code)
    - source    ->  tot_down_num    ->  value
    - source    ->  {timestamp_day} -> day_down_num

Malformed file lines will be logged:
    - malformed ->  {filename}  ->  line

'''

def fetch_url(server, directory, url, request_timestamp):
    today = datetime.now()
    today = str(today.year) + str(today.month).zfill(2) + str(today.day).zfill(2)

    #Add limiting info to redis
    server.hincrby(url, "tot_down_num") # source    ->  tot_down_num    ->  value
    server.hincrby(url, today)          # source    ->  {timestamp_day} ->  day_down_num

    #Check if total number of download exceded
    try:
        if int(server.hget(url, "tot_down_num")) > MAX_SOURCE_DOWNLOAD or int(server.hget(url, today)) > MAX_SOURCE_DOWNLOAD_PER_DAY: 
            logging.warning(url + "," + str(time()) + "," + "downloaded:{}".format(int(server.hget(url, "tot_down_num"))) + "," + "downloaded_today:{}".format(int(server.hget(url, today))))
            return
    except TypeError: #Key do not exists
        pass

    # perform request
    try:
        req = requests.get(url, stream=True, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        logging.warning(url + "," + str(time()) + "," + "timeout" )
        server.hset(url, request_timestamp, 'timeout')
        return
    except:
        logging.warning(url + "," + str(time()) + "," + "connectionError" )
        server.hset(url, request_timestamp, 'connectionError')
        return

    status_code = req.status_code
    if status_code >= 300:
        logging.warning(url + "," + str(time()) + "," + str(status_code))
        return

    #Download the remote binary
    block_size = 512
    bin_file = bytearray()
    for chunk in req.iter_content(chunk_size=block_size):
        if not chunk:
            break
        bin_file.extend(chunk)

    # Compute usefull fields

    now = time()
    sha1_obj = hashlib.sha1()
    sha1_obj.update(bin_file)
    the_hash = sha1_obj.hexdigest()

    filename = the_hash

    if len(server.keys(the_hash)) == 1: #hash already present
        server.sadd(the_hash, (url, now, status_code))
        logging.warning(url + "," + str(time()) + "," + str(status_code) + "," + "hash_already_present")
        return

    server.sadd(the_hash, (url, now, request_timestamp, status_code))

    subdir = os.path.join(directory, filename[:8])
    if not os.path.isdir(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, filename)

    # Write binary on disk
    with open(path, 'wb') as binary_f:
        binary_f.write(bin_file)



def fetch_ip(server, directory, options, request_timestamp):
    today = datetime.now()
    today = str(today.year) + str(today.month).zfill(2) + str(today.day).zfill(2)
    tempdir = os.path.join(directory, 'temp')

    #Add limiting info to redis
    server.hincrby(ip, "tot_down_num") # source    ->  tot_down_num    ->  value
    server.hincrby(ip, today)          # source    ->  {timestamp_day} ->  day_down_num

    #Check if total number of download exceded
    try:
        if int(server.hget(ip, "tot_down_num")) > MAX_SOURCE_DOWNLOAD or int(server.hget(ip, today)) > MAX_SOURCE_DOWNLOAD_PER_DAY: 
            logging.warning(ip + "," + str(time()) + "," + "downloaded:{}".format(int(server.hget(ip, "tot_down_num"))) + "," + "downloaded_today:{}".format(int(server.hget(ip, today))))
            return
    except TypeError: #Key do not exists
        pass

    for option in options:
        proto = option['proto']

        if proto == 'tftp':
            #print('>tftp')
            try:
                address = option['-g']
                filename = option['-r']
                temppath = os.path.join(tempdir, filename)
            except KeyError:
                continue
            try:
                #print(tftp_command.format(fnl=temppath, fnr=filename, addr=address))
                if tftp_command.format(fnl=temppath, fnr=filename, addr=address) in all_exec_cmd:
                    continue
                else:
                    all_exec_cmd.add(tftp_command.format(fnl=temppath, fnr=filename, addr=address))
                signal.alarm(TIMEOUT)
                osCall = check_call([tftp_command.format(fnl=temppath, fnr=filename, addr=address)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 
                signal.alarm(0)
                print('>executed tftp')
            except CalledProcessError:
                logging.warning(address+'/'+filename + "," + str(time()) + "," + "connectionError" )
                #print('>error tftp')
            except TimeoutException:
                logging.warning(address+'/'+filename + "," + str(time()) + "," + "connectionError" )
                #print('>error tftp')

        elif proto == 'wget':
            #print('>wget')
            if '' not in option:
                continue
            address = option['']
            if 'http' not in address:
                continue
            temppath = os.path.join(tempdir, 'wget_temp_bin')
            try:
                #print(wget_command.format(addr=address))
                if wget_command.format(addr=address) in all_exec_cmd:
                    continue
                else:
                    all_exec_cmd.add(wget_command.format(addr=address))
                osCall = check_call([wget_command.format(addr=address)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 
                print('>executed wget')
            except CalledProcessError:
                logging.warning(address + "," + str(time()) + "," + "connectionError" )
                #print('>error wget')

        elif proto == 'curl':
            #print('>curl')
            if '-O' in option:
                address = option['-O']
            elif '' in option:
                address = option['']
            else:
                continue
            
            if 'http' not in address:
                continue
            temppath = os.path.join(tempdir, 'curl_temp_bin')
            try:
                #print(curl_command.format(addr=address))
                if curl_command.format(addr=address) in all_exec_cmd:
                    continue
                else:
                    all_exec_cmd.add(curl_command.format(addr=address))
                osCall = check_call([curl_command.format(addr=address)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 
                print('>executed curl')
            except CalledProcessError:
                logging.warning(address + "," + str(time()) + "," + "connectionError" )
                #print('>error curl')

        elif proto == 'nc':
            #print('>nc')
            if '' not in option:
                continue
            cmd = option['']
            ip_port = reg_ip.search(cmd).group(0)
            if not ip_port:
                continue

            temppath = os.path.join(tempdir, 'nc_temp_bin')
            try:
                #print(nc_command.format(addr=ip_port, fn=temppath))
                if nc_command.format(addr=ip_port, fn=temppath) in all_exec_cmd:
                    continue
                else:
                    all_exec_cmd.add(nc_command.format(addr=ip_port, fn=temppath))
                osCall = check_call([nc_command.format(addr=ip_port, fn=temppath)], stdin=PIPE, stdout=PIPE, bufsize=1, shell=True) 
                print('>executed nc')
            except CalledProcessError:
                logging.warning(ip_port + "," + str(time()) + "," + "connectionError" )
                #print('>error nc')

        else:
            print(options)


        continue
        # recover the bin
        with open(temppath, 'rb') as fbin:
            bin_file = fbin.read()

            # Compute usefull fields
            now = time()
            sha1_obj = hashlib.sha1()
            sha1_obj.update(bin_file)
            the_hash = sha1_obj.hexdigest()

            filename = the_hash

            if len(server.keys(the_hash)) == 1: #hash already present
                server.sadd(the_hash, (url, now))
                logging.warning(url + "," + str(time()) + "," + "hash_already_present")
                return

            server.sadd(the_hash, (url, now, request_timestamp))

            subdir = os.path.join(directory, filename[:8])
            if not os.path.isdir(subdir):
                os.mkdir(subdir)
            path = os.path.join(subdir, filename)

            # Write binary on disk
            with open(path, 'wb') as binary_f:
                binary_f.write(bin_file)

        #remove temp file
        os.remove(temppath)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="The filename containing all the url to process")
    parser.add_argument('-d', '--directory', required=True, help="the directory in which the fetched url will be stored")
    args = parser.parse_args()

    # REDIS #
    #serv_bin = redis.StrictRedis(
    #        host='localhost',
    #        port=REDIS_PORT,
    #        db=REDIS_DB)
    serv_bin = None

    logging.basicConfig(filename='fetcher.log',level=logging.WARNING)

    with open(args.filename, 'r') as f:
        lines = f.read().splitlines()

    for i, line in enumerate(lines):
        dico = ast.literal_eval(line)
        timestamp = dico['timestamp']
        url_or_option = dico['type']
        print("progress: "+str(i)+"/"+str(len(lines)-1)+": {}%".format(int(i/len(lines)*100)), sep=' ', end='\r', flush=True)
        if url_or_option == 'url':
            continue
            fetch_url(serv_bin, args.directory, dico['url'], timestamp)
        elif url_or_option == 'option':
            fetch_ip(serv_bin, args.directory, dico['option'], timestamp)
    

if __name__ == "__main__":
    main()
