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

# REDIS #
serv_timestamp = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=2)
serv_ip = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=1)

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

    echo_session = 0
    noecho_session = 0

    session_without_cred = 0
    #cred -> occ
    dic_occ = {}
    #cred -> [ip]
    dic_cred_ip = {}
    #cred -> occ_uniqIP
    dic_occ_ip = {}


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
            
            #echo
            if session['echo'] == True:
                echo_session += 1
            elif session['echo'] == False:
                noecho_session += 1
            elif session['echo'] is None:
                noecho_session += 1
            else:
                pass

            #ranking
            array_remote = session_remote.split('\n')
            array_blackhole = session_blackhole.split('\n')

    
            if len(array_remote) < 2:
                #No command after login
                session_without_cred += 1
                continue

            cred, _ = extract_login_and_cmds(array_remote, array_blackhole)
            username = cred[0]
            password = cred[1]

            if username is None or password is None:
                # Session without password and username
                session_without_cred += 1
                continue

            try:
                dic_occ[cred] += 1
                if ip_remote in dic_cred_ip[cred]:
                    pass
                else:
                    dic_cred_ip[cred].add(ip_remote)
                    dic_occ_ip[cred] += 1
            except KeyError as e:
                dic_occ[cred] = 1
                dic_cred_ip[cred] = set(ip_remote)
                dic_occ_ip[cred] = 1

    #ECHO
    print("Number of ECHO sessions:\t\t{}\nNumber of noEcho sessions:\t\t{}\nTotal number of TELNET sessions:\t{}".format(echo_session, noecho_session, tot_ip_num))

    sorted_dic = sorted(dic_occ.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dic_uniq = sorted(dic_occ_ip.items(), key=operator.itemgetter(1), reverse=True)
    #pprint(sorted_dic)
    to_write = { 'ranking': str(sorted_dic),
            'ranking_uniq': str(sorted_dic_uniq),
             #'session_without_return_in_cred': session_without_return_in_cred['num'], 
            #'telnet_parsing_not_consistent': session_parse_error, 
            'tot_number_of_session': tot_ip_num, 
            'session_without_cred': session_without_cred,
            'echo_session': echo_session,
            'noecho_session': noecho_session}
    with open("make_stats_telnet_credentials_ranking.output", 'w') as f:
        f.write(str(to_write))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    parser.add_argument('-plot', '--plot', required=False, default=False, help='plot the data')
    args = parser.parse_args()

    make_stat()

