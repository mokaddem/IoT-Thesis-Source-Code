#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

'''
#
'''

import sys
import argparse
import redis
import operator
import struct, socket
from datetime import datetime
import csv
from pprint import pprint
import ast
from statistics import mean, median, pstdev, pvariance
sys.path.append('../../../')
from put_in_redis import Entry


# CONFIG #
dataset = "blackhole27"
fetch_command = ['tftp', 'wget', 'curl', 'nc']
ACCEPTABLE_WINDOW = 60*60*24 #1j


# REDIS #
serv_timestamp = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=6)
serv_ip = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=5)
serv_packets = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=11)
serv_ip_matching_isn = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=7)


def extract_login_and_cmds(Rsess, Bsess):
    expected_user = Rsess[0]
    expected_pass = Rsess[1]
    flag_pass = False
    flag_user = False
    flag_num = 0
    user_black = ""

    pot_cmds = []
    all_cmds = []
    for item in Bsess:
        if len(item) < 1:
            continue
        if 'Password: 'in item:
            flag_pass = True
            flag_num += 1
            #can't check on pswd because not echoed
        if 'Username: ' in item:
            flag_user = True
            flag_num += 1
            user_black = item.split('Username: ')[1]
            user_black = user_black
        if item[0] == '>':
            pot_cmds += [item[1:]]

    #cred
    if not (flag_pass and flag_user):
        cred = (None, None)
        if len(pot_cmds) == 0:
            return cred, [x for x in Rsess[flag_num:]]
        else:
            #not a valid session
            return (None, None), None

    username = ""
    password = None

    if expected_user == user_black:
        username = user_black
        password = expected_pass
    else:
        username = user_black

    #cmds
    for cmd in pot_cmds:
        if cmd in Rsess:
            if cmd == '\r' or cmd == '':
                pass
            else:
                cmd = cmd.strip('\r')
            all_cmds += [cmd]
        else:
            pass
    for unk in Rsess[:3]:
        if (unk not in pot_cmds) and (unk != user_black) and password is None:
            password = unk

    username = username.strip('\r')
    username = "(none)".encode('utf8') if username == "" else username.encode('utf8')
    password = "(none)".encode('utf8') if (password == "" or password is None or password == "\r") else password.strip('\r').encode('utf8')
    cred = (username, password)
    return cred, all_cmds


def make_stat():
    print("Computing Stats")

    #cred -> occ
    session_without_cred = 0
    all_sess_freq = []

    iter_num = 0
    all_ips = serv_ip.keys('*.*.*.*')
    tot_ip_num = len(all_ips)

    for ip in all_ips:
        if(iter_num % int(tot_ip_num/100) == 0):
            print("progress: {}%".format(int(iter_num/tot_ip_num*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        sess_freq = {}
        sess_freq['isn'] = []
        sess_freq['cred'] = []
        sess_freq['distri'] = []

        for timestamp, _ in serv_ip.hscan_iter(ip):
            timestamp = timestamp.decode('utf-8')
            session = serv_timestamp.smembers(timestamp).pop()
            session = ast.literal_eval(session.decode('utf-8'))
            ip_remote = session['ip_remote']
            ip_blackhole = session['ip_blackhole']
            session_remote = session['session_remote']
            session_blackhole = session['session_blackhole']

            sess_freq['ip'] = ip_remote

            if serv_ip_matching_isn.exists(ip_remote):
                sess_freq['isn'].append(timestamp)
            
            array_remote = session_remote.split('\n')
            array_blackhole = session_blackhole.split('\n')

            if len(array_remote) < 2:
                session_without_cred += 1
                continue

            cred, cmds = extract_login_and_cmds(array_remote, array_blackhole)
            username = cred[0]
            password = cred[1]

            if username is None or password is None:
                # Session without password and username
                session_without_cred += 1
                continue
            else:
                #compare if IP has already contacted but with a different port
                sess_freq['cred'] += [timestamp]

                for com in fetch_command:
                    for individual_command in cmds:
                       if individual_command.find(com) > -1:#found one matching -> distribute malware
                           sess_freq['distri'] += [timestamp]
                                                                                                                          

        all_sess_freq.append(sess_freq)

    to_write = { 
            'all_sess_freq': all_sess_freq
            }

    with open("make_stats_session_freq.output", 'w') as f:
        f.write(str(to_write))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    parser.add_argument('-plot', '--plot', required=False, default=False, help='plot the data')
    args = parser.parse_args()
    
    make_stat()
