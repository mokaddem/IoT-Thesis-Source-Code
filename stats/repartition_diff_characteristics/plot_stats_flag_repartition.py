#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, HourLocator, AutoDateLocator, AutoDateFormatter, MinuteLocator
import ast
from pprint import pprint
from collections import OrderedDict
import sys
import numpy as np
import math
from numpy import arange
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"
THRESHOLD_IGNORE = 0
windowS = datetime(2017, 2, 1, 0, 0, 0)
windowE = datetime(2017, 2, 1, 3, 0, 0)

maping_flag_meaning = {
        '0x00000002': "SYN",
        '0x00000004': "RST",
        '0x00000010': "ACK",
        '0x00000011': "FIN-ACK",
        '0x00000012': "SYN-ACK",
        '0x00000014': "RST-ACK",
        '0x00000018': "PSH-ACK",
        '0x00000019': "FIN-PSH-ACK",
        '0x00000052': "SYN-ACK-ECE",
        '0x000000c2': "SYN-ECN-CWR",
        '0x00000098': "PSH-ACK-CWR",
        '0x00000635': "FIN-RST-URG-Reserved"
        }

with open("make_stats_flags_repartition.output", 'r') as f:
    temp = f.read()

baseList = ast.literal_eval(temp)

isn_dico = baseList[0]
flags_dico = baseList[1]
flags_timestamp_dico = baseList[2]

'''
    FLAGS DICO
'''
print("Preparing data")

arr_plot = []
for flag, dico_isn in flags_dico.items():
    to_plot = []
    for isn, num in dico_isn.items():
        to_plot.append((isn, num))
    to_plot.sort(key=lambda x: x[0])

    to_plot1 = []
    to_plot2 = []
    for isn, num in to_plot:
        if num < THRESHOLD_IGNORE:
            continue
        to_plot1.append(isn)
        to_plot2.append(num)
    arr_plot.append([flag, [to_plot1, to_plot2]])

arr_plot.sort(key=lambda x: x[0])
    

#plot

print("plotting")

#fig, ax = plt.subplots(gridspec_kw = {'left':0.45, 'top':0.95, 'right':0.98})
fig, axs = plt.subplots(nrows=math.ceil(len(flags_dico.keys())/3.), ncols=3, gridspec_kw = {'hspace': 0.88})

i = 0
for row in axs:
    for ax in row:
        if i >= len(arr_plot):
            break
        ax.plot(arr_plot[i][1][0], arr_plot[i][1][1], linestyle='None', marker='o')
        #ax.bar(arr_plot[i][1][0], arr_plot[i][1][1], align='center')
    
        #xtick_locator = AutoDateLocator()
        #xtick_formatter = AutoDateFormatter(xtick_locator)
        #ax.xaxis.set_major_locator(xtick_locator)
        #ax.xaxis.set_major_formatter(xtick_formatter)
        
        ax.set_title(arr_plot[i][0] + ": " + maping_flag_meaning[arr_plot[i][0]])
        #ax.set_yticks([0,1,2])
        #ax.set_ylim([-1,3])
        ax.xaxis.grid(True, which='both')
        ax.yaxis.grid(True)
        #ax.set_xlabel("Time")
        i += 1


fig.suptitle("Repartition of the ISN for different tcp flags between " + windowS.strftime('%c')+" and "+windowE.strftime('%c'), fontsize=14, fontweight='bold')
fig.canvas.draw()


plt.show()

##################################################################################
'''
    FLAGS DICO TIMESTAMP
'''
arr_plot = []
for flag, all_isn in flags_timestamp_dico.items():
    date = []
    val = []
    for [d, v] in all_isn:
        cur_date = datetime.fromtimestamp(d)
        if windowS <= cur_date <= windowE:
            pass
        date.append(cur_date)
        val += [v]
    arr_plot.append([flag, [date, val]])
arr_plot.sort(key=lambda x: x[0])

fig, axs = plt.subplots(nrows=math.ceil(len(flags_dico.keys())/3.), ncols=3, gridspec_kw = {'hspace': 0.88})
i = 0
uni_ax = None
for row in axs:
    for ax in row:
        if i >= len(arr_plot):
            break   

        ax.plot(arr_plot[i][1][0], arr_plot[i][1][1], linestyle='None', marker='o', markersize=4)

        minutes_10 = MinuteLocator(interval=10)
        minutes_2 = MinuteLocator(interval=2)
        ax.xaxis.set_major_locator(minutes_10)
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        ax.xaxis.set_minor_locator(minutes_2)
        ax.grid(True)
        #fig.autofmt_xdate()

        if uni_ax is None:
            uni_ax = ax.get_xticks()

        ax.set_xticks(uni_ax)
        ax.set_ylabel("ISN value")
        ax.set_xlabel("Date")
        for label in ax.get_xmajorticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment("right")
        ax.set_title(arr_plot[i][0] + ": " + maping_flag_meaning[arr_plot[i][0]])

        i += 1
    
fig.suptitle("ISN over time from the blackhole between "+windowS.strftime('%c')+" and "+windowE.strftime('%c') + " for different TCP flags", fontsize=14, fontweight='bold')
plt.show()
