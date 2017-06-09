#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from pprint import pprint
from datetime import datetime
from datetime import timedelta
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, MinuteLocator
import matplotlib.pyplot as plt
import ast
import sys
import socket, struct
from statistics import mean, median, pstdev, pvariance

THRESHOLD_NOISE = 1000

#annotate bars
def autolabel(rects, thres_annot, ax):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        x_val = int(rect.get_x() + rect.get_width()/2.)
        if x_val not in [0, xxxxxxxxxxxxx, yyyyyyyyyyyy, zzzzzzzzzzz]:
            continue
        if height > thres_annot:
            ax.text(rect.get_x() + rect.get_width()/2., 10+height,
                    "{} -> {}".format(int(x_val), socket.inet_ntoa(struct.pack('!L', int(x_val)))),
                ha='center', va='bottom')


with open("make_stats_isn_overtime.output", "r") as f:
    temp = f.read()

baseList = ast.literal_eval(temp)

all_isn = baseList[0]
isn_dico = baseList[1]
dico_val_date = {}

date = []
val = []

windowS = datetime(2017, 2, 1, 0, 0, 0)
windowE = datetime(2017, 2, 1, 3, 0, 0)

for [d, v] in all_isn:
    cur_date = datetime.fromtimestamp(d)
    if windowS <= cur_date <= windowE:
        pass
    date.append(cur_date)
    val += [v]

fig, ax = plt.subplots()
ax.plot(date, val, marker='o', markersize=4, linestyle='None')

#text_info = ""
#text_info += "Total number of unique ip: {}".format(tot_ip)
#fig.text(0.75, .75, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})



minutes_10 = MinuteLocator(interval=10)
minutes_2 = MinuteLocator(interval=2)
ax.xaxis.set_major_locator(minutes_10)
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
ax.xaxis.set_minor_locator(minutes_2)
ax.grid(True)
fig.autofmt_xdate()


plt.ylabel("ISN value")
plt.xlabel("Date")
plt.title("ISN over time from the blackhole between "+windowS.strftime('%c')+" and "+windowE.strftime('%c'))

plt.show()

isn_array = []
num_array = []
isn_array_noise = []
num_array_noise = []
noise_to_sort = []
for isn, num in isn_dico.items():
    if num < THRESHOLD_NOISE:
        noise_to_sort.append((isn, num))
    else:
        isn_array += [isn]
        num_array += [num]

noise_to_sort.sort(key=lambda x: x[0])
for isn, num in noise_to_sort:
    isn_array_noise += [isn]
    num_array_noise += [num]

fig, ax = plt.subplots()
noise = ax.plot(isn_array_noise, num_array_noise, color='grey', alpha=0.5)
bar = ax.bar(isn_array, num_array, align='center', width=5000000)
ax.set_yscale("log")

autolabel(bar, 10**4, ax)

ax.grid(True)
plt.ylabel("Occurences")
plt.xlabel("ISN value")
plt.title("Occurences of ISN from the blackhole")
plt.legend(["ISN < {} -> noise".format(THRESHOLD_NOISE), "ISN > {} -> interesting value".format(THRESHOLD_NOISE)])
plt.show()
