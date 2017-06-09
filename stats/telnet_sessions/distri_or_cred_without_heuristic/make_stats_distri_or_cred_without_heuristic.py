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


# CONFIG #
dataset = "blackhole27"
ACCEPTABLE_WINDOWS = [
        1,
        60,
        60*5,
        60*15,
        60*30,
        60*60*1,
        60*60*6,
        60*60*24,
        60*60*24*3
        ]
ACCEPTABLE_WINDOWS = [
        10,
        60,
        60*2,
        60*3,
        60*4,
        60*5,
        60*60*24,
        60*60*24*7,
        60*60*24*7*4
        ]


# REDIS #
serv_timestamp = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=6)
serv_ip = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=5)
serv_heuri = redis.StrictRedis(
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


def make_stat(win):
    print("Computing Stats")

    #cred -> occ
    telnet_with_isn = {}
    num_telnet_with_isn = 0
    num_telnet_with_no_isn = 0
    session_without_cred = 0

    iter_num = 0
    all_sessions = serv_timestamp.keys('??????????.?????????')
    tot_ip_num = len(all_sessions)

    for timestamp in all_sessions:
        if(iter_num % int(tot_ip_num/100) == 0):
            print("progress: {}%".format(int(iter_num/tot_ip_num*100)), sep=' ', end='\r', flush=True)
        iter_num += 1

        for session in serv_timestamp.smembers(timestamp):
            session = ast.literal_eval(session.decode('utf-8'))
            ip_remote = session['ip_remote']
            ip_blackhole = session['ip_blackhole']
            session_remote = session['session_remote']
            session_blackhole = session['session_blackhole']
            
            array_remote = session_remote.split('\n')
            array_blackhole = session_blackhole.split('\n')

            if len(array_remote) < 2:
                session_without_cred += 1
                continue

            cred, _ = extract_login_and_cmds(array_remote, array_blackhole)
            username = cred[0]
            password = cred[1]

            if username is None or password is None:
                # Session without password and username
                session_without_cred += 1
                continue
            else:
                #compare if isn=ip.dst
                all_timestamp_isn = serv_heuri.smembers(ip_remote)
                if len(all_timestamp_isn) == 0:
                    continue

                num_telnet_with_no_isn += 1 # add 1, if match detected, will be decremented
                for timestamp_isn in all_timestamp_isn:
                    if abs(float(timestamp_isn) - float(timestamp)) <= win:
                        num_telnet_with_isn += 1
                        num_telnet_with_no_isn -= 1
                        telnet_with_isn[ip_remote] = timestamp
                        break


    to_write = { 'telnet_with_isn': str(telnet_with_isn),
            'num_telnet_with_isn': num_telnet_with_isn,
            'num_telnet_with_no_isn': num_telnet_with_no_isn
            }
    print('res')
    print(num_telnet_with_isn, num_telnet_with_no_isn)

    with open("make_stats_distri_or_cred_without_heuristic_"+str(win)+".output", 'w') as f:
        f.write(str(to_write))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    parser.add_argument('-plot', '--plot', required=False, default=False, help='plot the data')
    args = parser.parse_args()
    
    for win in ACCEPTABLE_WINDOWS:
        make_stat(win)
