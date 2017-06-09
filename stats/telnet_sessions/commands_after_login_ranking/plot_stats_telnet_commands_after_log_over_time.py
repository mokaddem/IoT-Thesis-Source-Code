#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
import ast
from pprint import pprint
import sys
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"
thres_om = 50

with open("make_stats_telnet_commands_after_log.output", 'r') as interesting_cmds:
    int_cmds = interesting_cmds.read()

dico = ast.literal_eval(int_cmds)
ranking = ast.literal_eval(dico['ranking'])
mapping_cmd_num = {}
cur_num = 1
for cmd, occ in ranking:
    if occ > thres_om:
        #mapping_cmd_num[cmd] = cur_num
        cur_num += 1

mapping_cmd_num['Others'] = 1
for cmd, occ in ranking:
    if occ > thres_om:
        mapping_cmd_num[cmd] = cur_num
        cur_num -= 1




with open("make_stats_telnet_commands_after_log_overtime.output", "r") as f:
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
showed_cmd = 0
temp_cmd_overtime = []
tot_num_cmd = 0
for cmd, timestamps in ranking.items():
    tot_num_cmd += 1
    if len(timestamps) > thres_om:
        sum_showed += len(timestamps)
        showed_cmd += 1
        if cmd not in mapping_cmd_num:
            mapping_cmd_num[cmd] = cur_num
            cur_num += 1
        for timestamp in timestamps:
            temp_cmd_overtime.append([datetime.fromtimestamp(float(timestamp)), mapping_cmd_num[cmd]])
    else:
        not_shown += 1
        not_shown_occ += len(timestamps)
        for timestamp in timestamps:
            temp_cmd_overtime.append([datetime.fromtimestamp(float(timestamp)), mapping_cmd_num['Others']])


mapping_cmd_num_rev = {}
for k,v in mapping_cmd_num.items():
    mapping_cmd_num_rev[v] = k

temp_cmd_overtime.sort(key= lambda x: x[0])

for tab in temp_cmd_overtime:
    d, val = tab
    dates_x.append(d)
    y.append(val)


text_info = ""
text_info += "Number of invalid session: {} ({:.2%})\n".format(invalid_session, invalid_session/tot_number_of_session)
text_info += "Number of session without commands: {} ({:.2%})\n".format(session_without_command, session_without_command/tot_number_of_session)
text_info += "Shown unique commands: {} ({:.2%})\n".format(showed_cmd, showed_cmd/tot_num_cmd)
text_info += "# of unique commands in \'Others\': {} ({:.2%})".format(not_shown, not_shown/tot_num_cmd)


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

fig, ax = plt.subplots(gridspec_kw = {'left':0.45, 'top':0.95, 'right':0.98})
#fig, ax = plt.subplots()

ax.plot(dates_x, y, linestyle='None', marker='o')

# every monday
mondays = WeekdayLocator(MONDAY)
months = MonthLocator(range(1, 13), bymonthday=1)
monthsFmt = DateFormatter("%d %b '%y")
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_major_formatter(monthsFmt)
ax.autoscale_view()

fig.autofmt_xdate()

ax.set_title("Repartition of the commands used during a telnet sessions over time (filtered: <"+str(thres_om)+")")
ax.yaxis.grid(True, which='both')
ax.xaxis.grid(True, which='both')
ax.set_xlabel("Date")
ax.set_ylabel("Commands")


ax.set_yticks([x for x in range(len(mapping_cmd_num)+1)])

fig.canvas.draw()

labels = [i.get_text() for i in ax.get_yticklabels()]
for i, lb in enumerate(labels):
    lb = int(lb)
    if lb not in mapping_cmd_num_rev:
        labels[i] = ""
    else:
        labels[i] = mapping_cmd_num_rev[lb]
ax.set_yticklabels(labels)

fig.text(.05, .2, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})

plt.show()
