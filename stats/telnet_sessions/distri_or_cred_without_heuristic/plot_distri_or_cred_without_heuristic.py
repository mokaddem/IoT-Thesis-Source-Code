#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
import ast
import sys
import numpy as np
from pprint import pprint

M = 60
H = 60*60

sizes = []
windows = []
#read 1
for winsize, win_txt in zip([10, M, 2*M, 3*M, 4*M, 5*M, H, 24*H, 7*24*H], ['10s', '60s', '1m', '3m', '4m', '5m', '24h', '7days', '1month']):
    with open("outputs/make_stats_distri_or_cred_without_heuristic_"+str(winsize)+".output", "r") as f:
        temp = f.read()
        baseDico = ast.literal_eval(temp)
        num_telnet_with_no_isn = baseDico['num_telnet_with_no_isn']
        num_telnet_with_isn = baseDico['num_telnet_with_isn']
        num_tot = num_telnet_with_no_isn + num_telnet_with_isn
        telnet_with_isn = baseDico['telnet_with_isn']
        windows += [win_txt]
        sizes.append([num_telnet_with_isn/num_tot, num_telnet_with_no_isn/num_tot])


fig, axs = plt.subplots(nrows=3, ncols=3)
fig.suptitle("Percentages of telnet sessions having the isn=IP.dst property", fontsize=14, fontweight='bold')
axs = [x for x in axs[0]] + [x for x in axs[1]] + [x for x in axs[2]]
explode = [0.05, 0.05]
labels = ['isn=IP.dst', 'isn!=IP.dst']
for ax, size, win_txt in zip(axs, sizes, windows):
    ax.set_title("Window of " + win_txt)
    ax.pie(size, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=0)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()


