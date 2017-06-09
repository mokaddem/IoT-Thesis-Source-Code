#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, DayLocator
import ast
from pprint import pprint
import sys
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"
thres_om = 200

with open("make_stats_telnet_credentials_ranking.output", 'r') as interesting_cmds:
    int_cmds = interesting_cmds.read()

dico = ast.literal_eval(int_cmds)
ranking = ast.literal_eval(dico['ranking'])
mapping_cred_num = {}
cur_num = 1
for cred, occ in ranking:
    if occ > thres_om:
        cur_num += 1

mapping_cred_num['Others'] = 1
for cred, occ in ranking:
    if occ > thres_om:
        mapping_cred_num[cred] = cur_num
        cur_num -= 1


with open("make_stats_telnet_credentials_overtime.output", "r") as f:
    temp = f.read()

dates_x = []
y = []

dico = ast.literal_eval(temp)
ranking = ast.literal_eval(dico['overtime'])
tot_number_of_session = int(dico['tot_number_of_session'])
session_without_command = int(dico['session_without_command'])
invalid_session = int(dico['invalid_session'])
session_with_command = tot_number_of_session - session_without_command

not_shown = 0
not_shown_occ = 0
sum_showed = 0
showed_cred = 0
temp_cred_overtime = []
tot_num_cred = 0
for cred, timestamps in ranking.items():
    tot_num_cred += 1
    if len(timestamps) > thres_om:
        sum_showed += len(timestamps)
        showed_cred += 1
        if cred not in mapping_cred_num:
            print( cred)
            mapping_cred_num[cred] = cur_num
            cur_num += 1
        for timestamp in timestamps:
            temp_cred_overtime.append([datetime.fromtimestamp(float(timestamp)), mapping_cred_num[cred]])
    else:
        not_shown += 1
        not_shown_occ += len(timestamps)
        for timestamp in timestamps:
            temp_cred_overtime.append([datetime.fromtimestamp(float(timestamp)), mapping_cred_num['Others']])

mapping_cred_num_rev = {}
for k,v in mapping_cred_num.items():
    mapping_cred_num_rev[v] = k
temp_cred_overtime.sort(key= lambda x: x[0])

for tab in temp_cred_overtime:
    d, val = tab
    dates_x.append(d)
    y.append(val)


text_info = ""
text_info += "Number of invalid session: {} ({:.2%})\n".format(invalid_session, invalid_session/tot_number_of_session)
text_info += "Number of session without commands: {} ({:.2%})\n".format(session_without_command, session_without_command/tot_number_of_session)
text_info += "Shown unique commands: {} ({:.2%})\n".format(showed_cred, showed_cred/tot_num_cred)
text_info += "# of unique commands in \'Others\': {} ({:.2%})".format(not_shown, not_shown/tot_num_cred)


#plot

#annotate bars
def autolabel(rects, ax):
    """
    Attach a text label above each bar displaying its height
    """

    (x_left, x_right) = ax.get_xlim()
    x_width = x_right - x_left

    for rect in rects:
        width = rect.get_width()
        label_position_x = width + x_width * 0.01
        value = int(rect.get_y()+rect.get_height()/2.)
        ax.text(width*1.85, value+0.5*rect.get_height(), 
                "{} - {:.2%}".format(int(width), float(width)/float(session_with_command)),
                ha='center', va='bottom')

print("plotting")

fig, ax = plt.subplots()

ax.plot(dates_x, y, linestyle='None', marker='o')

# every monday
mondays = WeekdayLocator(MONDAY)
months = MonthLocator(range(1, 13), bymonthday=1)
days = DayLocator(interval=1)
monthsFmt = DateFormatter("%d %b '%y")
daysFmt = DateFormatter("%d/%m/%y")
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_major_formatter(monthsFmt)
ax.xaxis.set_minor_locator(days)
ax.autoscale_view()

fig.autofmt_xdate()

ax.set_title("Repartition of the credentials used during a telnet sessions over time (filtered: <"+str(thres_om)+")")
ax.yaxis.grid(True, which='both')
ax.xaxis.grid(True, which='both')
ax.set_xlabel("Date")
ax.set_ylabel("Commands")


ax.set_yticks([x for x in range(len(mapping_cred_num)+1)])

fig.canvas.draw()

labels = [i.get_text() for i in ax.get_yticklabels()]
for i, lb in enumerate(labels):
    lb = int(lb)
    if lb not in mapping_cred_num_rev:
        labels[i] = ""
    else:
        labels[i] = mapping_cred_num_rev[lb]
ax.set_yticklabels(labels)


plt.show()


fig, ax = plt.subplots()

ax.plot(dates_x, [1 for x in range(len(dates_x))], linestyle='None', marker='s', markersize='10')

# every monday
mondays = WeekdayLocator(MONDAY)
months = MonthLocator(range(1, 13), bymonthday=1)
days = DayLocator(interval=1)
monthsFmt = DateFormatter("%d %b '%y")
daysFmt = DateFormatter("%d/%m/%y")
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_major_formatter(monthsFmt)
ax.xaxis.set_minor_locator(days)
#ax.xaxis.set_minor_formatter(daysFmt)
ax.autoscale_view()

fig.autofmt_xdate()
ax.yaxis.grid(True, which='both')
ax.xaxis.grid(True, which='both')
ax.yaxis.set_visible(False)

plt.show()
