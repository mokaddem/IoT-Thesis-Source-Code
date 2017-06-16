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
import time
from datetime import datetime, date
import csv
from pprint import pprint
import ast
import json
import re
from statistics import mean, median, pstdev, pvariance


# CONFIG #
dataset = "blackhole27"
TIMESLEEP = 60*60*1

# REDIS #
serv_temp_timestamp = redis.StrictRedis(
    host='localhost',
    port=6502,
    db=2)
serv_temp_ip = redis.StrictRedis(
    host='localhost',
    port=6502,
    db=1)

'''
try to get the protocol used
try to parse an ip
try to parse an url
'''
def extract_urls_or_ips(cmds, ip):
    parsed = []
    fetch_command = ['tftp', 'wget', 'curl', 'nc']
    regex_ip = "(\d{1,3}\.)(\d{1,3}\.)(\d{1,3}\.)(\d{1,3})(?=;|\s|\|)"
    regex_url = "((http|https)+(\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&%\$#\=~_\-]+))*))"
    reg_ip = re.compile(regex_ip)
    reg_url = re.compile(regex_url)

    f_cdm = []
    ips = []
    urls = []
    options = []
    for cmd in cmds:
        try:
            cmd = cmd.decode('ascii', 'backslashreplace')
        except AttributeError:
            pass
        # Used fetch command
        for f_c in fetch_command:
            index_found = cmd.find(f_c)
            if index_found > -1:#found one matching
                f_cdm.append(f_c)
                if f_c in ['tftp', 'wget', 'curl']: #search for options
                    cur_options = {'proto': f_c}
                    #index_end_of_command = cmd[index_found:].find('||')
                    test1 = cmd[index_found:].find('||')
                    test1 = test1 if test1 > 0 else 0
                    test2 = cmd[index_found:].find(';')
                    test2 = test2 if test2 > 0 else 0
                    index_end_of_command = test1 if test1 < test2 else test2
                    if index_end_of_command > 0:
                        index_end_of_command += index_found
                        complete_cmd = cmd[index_found+4:index_end_of_command].split(' ')[1:]
                    else:
                        index_end_of_command = cmd[index_found:].find(';')+index_found
                        complete_cmd = cmd[index_found+4:index_end_of_command].split(' ')[1:]

                    cur_key = ""
                    for option in complete_cmd:
                        if option.startswith('-'):
                            cur_key = option
                        elif option != "":
                            cur_options[cur_key] = option
                    options.append(cur_options)

                if f_c == "nc": #search for nc options
                    cur_options = {'proto': "nc"}
                    index_end_of_command = cmd[index_found:].find(';')+index_found
                    complete_cmd = cmd[index_found+2:index_end_of_command]
                    cur_key = ""
                    cur_options[cur_key] = complete_cmd
                    options.append(cur_options)

        ips = reg_ip.findall(cmd)
        urls_search = reg_url.findall(cmd)
        for res in urls_search:
            urls += [res[0]]

        ip_str = ""
        for i,ip in enumerate(ips):
            if i > 0:
                ip_str += ";"
            ip_str += ''.join(ip)

        url_str = ""
        for i,url in enumerate(urls):
            if i > 0:
                url_str += ";"
            url_str += ''.join(url)

        if len(ips) > 0 or len(urls) > 0:
                parsed.append((f_cdm, {'ips': ip_str, 'urls': url_str, 'options': options}))
    return parsed


def extract_login_and_cmds(Rsess, Bsess):
    expected_user = Rsess[0].encode('utf8')
    expected_pass = Rsess[1].encode('utf8')
    flag_pass = False
    flag_user = False
    user_black = None

    pot_cmds = []
    all_cmds = []
    for item in Bsess:
        if len(item) < 1:
            continue
        if 'Password: 'in item:
            flag_pass = True
            #can't check on pswd because not echoed
        if 'Username: ' in item:
            flag_user = True
            user_black = item.split('Username: ')[1].strip("\n")
            user_black = user_black.encode('utf-8')
        if item[0] == '>':
            pot_cmds += [item[1:]]

    #cred
    if not (flag_pass and flag_user):
        cred = (None, None)
        if len(pot_cmds) == 0:
            return cred, [x.encode('utf-8') for x in Rsess]
    username = None
    password = None

    if expected_user == user_black:
        username = user_black
        password = expected_pass
    else:
        username = user_black

    #cmds
    for cmd in pot_cmds:
        if cmd in Rsess:
            all_cmds += [cmd]
        else:
            pass
    for unk in Rsess[:3]:
        if (unk not in pot_cmds) and (unk != user_black) and password is None:
            password = unk

    cred = (username, password)
    all_cmds.reverse() #put command in right order
    return cred, all_cmds
        

def make_stat():
    print("Recovering URLs")

    urls = set()
    ips = set()
    options = []
    dico_fetch_command_used = {}
    all_sessions = serv_temp_timestamp.keys('??????????.?????????')
    session_without_command = 0
    session_with_command = 0
    session_with_fetching = 0
    tot_ip_num = len(all_sessions)
    for timestamp in all_sessions:

        command_after_log = []
        for session in serv_temp_timestamp.smembers(timestamp):
            session = ast.literal_eval(session.decode('utf-8'))
            ip_remote = session['ip_remote']
            ip_blackhole = session['ip_blackhole']
            session_remote = session['session_remote']
            session_blackhole = session['session_blackhole']
            
            #ranking
            array_remote = session_remote.split('\n')
            array_blackhole = session_blackhole.split('\n')

            if len(array_remote) < 3:
                #No command after login
                session_without_command += 1
                continue
            else:
                cred, cmds = extract_login_and_cmds(array_remote, array_blackhole)
                if (cmds is None) or len(cmds) == 0: #No command
                    session_without_command += 1
                    continue
                session_with_command += 1
                command_after_log += cmds

            extracted_array = extract_urls_or_ips(command_after_log, ip_remote)
            if len(extracted_array) > 0:
                session_with_fetching += 1

            for fetch_command, dico_address in extracted_array:
                for f_c in fetch_command:
                    try:
                        dico_fetch_command_used[f_c] += 1
                    except KeyError:
                        dico_fetch_command_used[f_c] = 1
                    
                for ip in dico_address['ips'].split(';'):
                    if ip != "":
                        ips.add((ip, timestamp))
                for url in dico_address['urls'].split(';'):
                    if url != "":
                        urls.add((url, timestamp))
                options.append((dico_address['options'], timestamp))


    to_write = { 'urls': str(urls),
            'ips': str(ips), 
            'fetch_command_used': str(dico_fetch_command_used),
            'session_without_command': session_without_command,
            'session_with_command': session_with_command,
            'session_with_fetching': session_with_fetching}
    pprint(to_write)

    with open("telnet_session_URL_extractor_live.output", 'w') as f:
        f.write(str(to_write))
    with open("extracted_urls_live.output", 'w') as f:
        dico1 = {'type': 'url'}
        for url in urls:
            dico1['timestamp'] = url[1]
            dico1['url'] = url[0]
            f.write(str(dico1)+"\n")
        dico2 = {'type': 'ip'}
        for ip in ips:
            dico2['timestamp'] = ip[1]
            dico2['ip'] = ip[0]
            f.write(str(dico2)+"\n")
        dico3 = {'type': 'option'}
        for option in options:
            dico3['timestamp'] = option[1]
            dico3['option'] = option[0]
            f.write(str(dico3)+"\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Makes stats about the frequency of IP within a acceptation window')
    args = parser.parse_args()
    
    while True:
        if len(serv_temp_timestamp.keys('*')):
            make_stat()

            to_write = {'timestamp': {}}
            for k in serv_temp_timestamp.keys():
                v = list(serv_temp_timestamp.smembers(k))[0].decode('utf8')
                k = k.decode('utf8')
                to_write['timestamp'][k] = v
            #for k in serv_temp_ip.keys():
            #    v = serv_temp_timestamp.hgetall(k)
            #    if len(v) == 0:
            #        continue
            #    print('-----------------')
            #    print(k,v)
            #    #v = v.decode('utf8')
            #    k = k.decode('utf8')
            #    to_write['ip'][k] = v
            #pprint(to_write)
            with open(str(date.today().isoformat()), 'w') as f:
                json.dump(to_write, f)
                #f.write(str(to_write))

            serv_temp_timestamp.flushdb()
            serv_temp_ip.flushdb()
            print('processed at ' + str(time.time()))
        else:
            print('No key present, sleeping '+str(TIMESLEEP)+'sec')
            time.sleep(TIMESLEEP)
