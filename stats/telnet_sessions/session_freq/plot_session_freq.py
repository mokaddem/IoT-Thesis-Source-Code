#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, HourLocator, AutoDateLocator, AutoDateFormatter
import ast
from pprint import pprint
from collections import OrderedDict
import sys
import numpy as np
from numpy import arange
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"

with open("make_stats_session_freq.output", 'r') as f:
    temp = f.read()

array = ast.literal_eval(temp)['all_sess_freq']

max_isn = 0
max_both_c = 0
max_both_ci = 0
max_cred = 0
max_both_d = 0
max_both_di = 0
max_distri = 0


mapping_num_type = {
        2: 'isn = ip.dst',
        1: 'Credential bruteforce',
        0: 'Malware distribution',
        }

dico_data = OrderedDict()
dico_data['max_isn'] = None
dico_data['max_both_c'] = None
dico_data['max_cred'] = None
dico_data['max_both_d'] = None
dico_data['max_distri'] = None

dico_name = OrderedDict()
dico_name['max_isn'] = ["Scanning only", None]
dico_name['max_both_c'] = ["Both Scanning and Credentials Bruteforce", None]
dico_name['max_cred'] = ["Credentials Bruteforce only", None]
dico_name['max_both_d'] = ["Both Scanning and Distributing Malware", None]
dico_name['max_distri'] = ["Distributing Malware only", None]

for ip in array:
    cred_timestamp_arr = ip['cred']
    isn_timestamp_arr = ip['isn']
    distri_timestamp_arr = ip['distri']
    ip_remote = ip['ip']

    if len(isn_timestamp_arr) == 0 and len(cred_timestamp_arr) == 0:
        continue
    '''isn'''
    #max isn
    if len(isn_timestamp_arr) > max_isn:
        max_isn = len(isn_timestamp_arr)
        dico_data['max_isn'] = ip
        dico_name['max_isn'][1]= ip_remote

    '''cred'''
    #max both
    if len(isn_timestamp_arr) > max_both_ci and len(cred_timestamp_arr) > max_both_c:
        max_both_ci = len(isn_timestamp_arr)
        max_both_c = len(cred_timestamp_arr)
        dico_data['max_both_c'] = ip
        dico_name['max_both_c'][1]= ip_remote
    #max cred
    if len(cred_timestamp_arr) > max_cred:
        max_cred = len(cred_timestamp_arr)
        dico_data['max_cred'] = ip
        dico_name['max_cred'][1]= ip_remote

    '''distri'''
    #max both
    if len(isn_timestamp_arr) > max_both_di and len(distri_timestamp_arr) > max_both_d:
        max_both_di = len(isn_timestamp_arr)
        max_both_d = len(distri_timestamp_arr)
        dico_data['max_both_d'] = ip
        dico_name['max_both_d'][1]= ip_remote
    #max cred
    if len(distri_timestamp_arr) > max_distri:
        max_distri = len(distri_timestamp_arr)
        dico_data['max_distri'] = ip
        dico_name['max_distri'][1]= ip_remote



#pprint(dico_data)
arr_plot = []
for name, ip in dico_data.items():
    #cred
    try:
        time_c = [ datetime.fromtimestamp(float(x)) for x  in ip['cred']]
    except ValueError:
        time_c = []
    y_c = [1 for i in time_c]

    #distri
    try:
        time_d = [ datetime.fromtimestamp(float(x)) for x  in ip['distri']]
    except ValueError:
        time_d = []
    y_d = [0 for i in time_d]

    #isn
    try:
        time_i = [ datetime.fromtimestamp(float(x)) for x  in ip['isn']]
    except ValueError:
        time_i = []
    y_i = [2 for i in time_i]


    #print(time_c)
    arr_plot.append({'x': [time_c, time_i, time_d], 'y': [y_c, y_i, y_d], 'name': name, 'sum':[len(y_d), len(y_c), len(y_i)]})


#plot

print("plotting")

#fig, ax = plt.subplots(gridspec_kw = {'left':0.45, 'top':0.95, 'right':0.98})
fig, axs = plt.subplots(nrows=len(dico_name), ncols=1, gridspec_kw = {'hspace': 0.88})

for ax, to_plot in zip(axs, arr_plot):
    ax.plot(to_plot['x'][0], to_plot['y'][0], linestyle='None', marker='o')
    ax.plot(to_plot['x'][1], to_plot['y'][1], linestyle='None', marker='v')
    ax.plot(to_plot['x'][2], to_plot['y'][2], linestyle='None', marker='*', markersize=16)

    xtick_locator = AutoDateLocator()
    xtick_formatter = AutoDateFormatter(xtick_locator)
    ax.xaxis.set_major_locator(xtick_locator)
    ax.xaxis.set_major_formatter(DateFormatter("%d/%m/%y %H:%M:%S"))
    
    ax.set_title(dico_name[to_plot['name']][0] + ": " + dico_name[to_plot['name']][1])
    ax.set_yticks([0,1,2])
    ax.set_ylim([-1,3])
    ax.xaxis.grid(True, which='both')
    ax.yaxis.grid(True)
    ax.set_xlabel("Time")

    ax2 = ax.twinx()
    ax2.set_ylabel("Sum")
    ax2.set_yticks([0,1,2])
    ax2.set_ylim([-1,3])
    ax2.set_yticklabels(to_plot['sum'])


fig.suptitle("Maximum of occurences for: ", fontsize=14, fontweight='bold')
fig.canvas.draw()


for ax in axs:
    labels = [i.get_text() for i in ax.get_yticklabels()]
    for i, lb in enumerate(labels):
        if lb == '':
            continue
        lb = int(lb)
        labels[i] = mapping_num_type[lb]
    ax.set_yticklabels(labels)
    labels = [i.get_text() for i in ax.get_xticklabels()]
    for i, lb in enumerate(labels):
        pass
    ax.set_xticklabels(labels, rotation=0)


#fig.text(.05, .2, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})

plt.show()
