#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
import ast
import sys
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"
thres_om = 50

with open("make_stats_telnet_commands_after_log.output", "r") as f:
    temp = f.read()

x = []
y = []
array_label = []
iteration = 0

dico = ast.literal_eval(temp)
# ranking := ((user, pass), occ)
ranking = ast.literal_eval(dico['ranking'])
tot_number_of_session = int(dico['tot_number_of_session'])
session_without_command = int(dico['session_without_command'])
invalid_session = int(dico['invalid_session'])
session_with_command = tot_number_of_session - session_without_command

not_shown = 0
not_shown_occ = 0
sum_showed = 0
for cmd, occ in ranking:
    if occ > thres_om:
        array_label.append(cmd)
        x.append(iteration)
        y.append(occ)
        sum_showed += occ
        iteration += 1
    else:
        not_shown += 1
        not_shown_occ += occ

text_info = "SESSION:\n"
text_info += "Total number of session: {}\n".format(tot_number_of_session)
text_info += "Number of invalid session: {} ({:.2%})\n".format(invalid_session, invalid_session/tot_number_of_session)
text_info += "Number of session with commands: {} ({:.2%})\n".format(session_with_command, session_with_command/tot_number_of_session)
text_info += "Number of session without commands: {} ({:.2%})\n".format(session_without_command, session_without_command/tot_number_of_session)
text_info += "Shown: {} ({:.2%})\n".format(sum_showed, sum_showed/session_with_command)
text_info += "Not shown: {} ({:.2%})\n".format(not_shown, not_shown_occ/session_with_command)


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

fig, ax = plt.subplots(gridspec_kw = {'left':0.45, 'top':0.95})

y_pos = np.arange(len(array_label))

bars = ax.barh(y_pos, y, align='center', color='gb')
ax.set_yticks(y_pos)
ax.set_yticklabels(array_label)
ax.invert_yaxis()


ax.set_xscale("log")
ax.xaxis.grid(True, which='both')

ax.set_ylabel("Commands used")
ax.set_xlabel("Occurences")
ax.set_title("Distribution of the commands used during a telnet session (filtered: <"+str(thres_om)+")")

fig.text(.65, .2, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})
autolabel(bars, ax)

plt.show()

