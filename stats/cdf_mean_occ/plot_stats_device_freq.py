#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import ast
import sys
#from make_stats_device_freq import ACCEPTATION_WINDOW, ONE_DAY
import numpy as np

ONE_DAY = 60*60*24 #1 day
ACCEPTATION_WINDOW = ONE_DAY*1 #1 day


#annotate curve
def autolabel2(ax):
    print('labeling')
    """tot_number_of_session
    Attach a text label above each bar displaying its height
    """
    to_label = [1,2,3,7,20]
    xy = ax.lines[0].get_xydata()
    for i, tab in enumerate(xy):
        x, y = tab
        if y <= 0:
            continue
        if x not in to_label: 
            continue
        to_label.remove(x)
        ax.text(x, y-0.03, 
                "({}, {:.2f})".format(int(x),y),
                ha='center', va='bottom')

with open("make_stats_freq_ip_cdf.output", "r") as f:
    temp = f.read()

baseList = ast.literal_eval(temp)

X = baseList[0]
Y = baseList[1]
dico_stat = baseList[2]

txt = ""
for stat, val in dico_stat.items():
    txt += stat + ": " + "{0:.2f}".format(val) + "\n"

#plot

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(X, Y)
ax.set_title("CDF of the mean(occurences IP.src) within the acceptation window ("+str(int(ACCEPTATION_WINDOW/ONE_DAY))+" day) per unique ip")
ax.yaxis.grid(True, which='both')
ax.set_xlabel("Occurence")
ax.set_ylabel("CDF")
ax.set_xscale('log')
fig.text(.7, .3, txt, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})

autolabel2(ax)

ax.set_xticks(ax.get_xticks())

plt.show()

