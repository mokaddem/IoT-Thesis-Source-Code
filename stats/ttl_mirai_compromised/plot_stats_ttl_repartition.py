#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
from pprint import pprint
import ast
import sys
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG
thres_annot = 50000

with open("make_stats_ttl_repartition.output", "r") as f:
    temp = f.read()

baseArray = ast.literal_eval(temp)
dico_ttl = baseArray[0]
dico_ttl_all = baseArray[1]
dico_ttl_session = baseArray[2]

#port 23 and 2323 and not icmp
combi_ttl = []
tot_usage = 0
for ttl, val in dico_ttl.items():
    combi_ttl.append([ttl, val])
    tot_usage += val
combi_ttl.sort(key=lambda x: int(x[0]))

#not icmp
combi_ttl_all = []
tot_usage_all = 0
for ttl, val in dico_ttl_all.items():
    combi_ttl_all.append([ttl, val])
    tot_usage_all += val
combi_ttl_all.sort(key=lambda x: int(x[0]))

#session
combi_ttl_session = []
tot_usage_session = 0
for ttl, val in dico_ttl_session.items():
    combi_ttl_session.append([ttl, val])
    tot_usage_session += val
combi_ttl_session.sort(key=lambda x: int(x[0]))


y = []
y_all = []
y_session = []
x = []
for tab in combi_ttl:
    x.append(tab[0])
    y.append(tab[1])

for tab in combi_ttl_all:
    y_all.append(tab[1])

for tab in combi_ttl_session:
    y_session.append(tab[1])

X = np.array(x)
Y = np.array(y)
Y_all = np.array(y_all)
Y_session = np.array(y_session)

#stat port 23 and 2323 and not icmp
dico_stat = {}
dico_stat["mean"] = mean(Y)
dico_stat["median"] = median(Y)
dico_stat["std_dev"] = pstdev(Y)
dico_stat["variance"] = pvariance(Y)
dico_stat["max"] = max(Y)

#not icmp
dico_stat_all = {}
dico_stat_all["mean"] = mean(Y_all)
dico_stat_all["median"] = median(Y_all)
dico_stat_all["std_dev"] = pstdev(Y_all)
dico_stat_all["variance"] = pvariance(Y_all)
dico_stat_all["max"] = max(Y_all)

#session
dico_stat_session = {}
dico_stat_session["mean"] = mean(Y_session)
dico_stat_session["median"] = median(Y_session)
dico_stat_session["std_dev"] = pstdev(Y_session)
dico_stat_session["variance"] = pvariance(Y_session)
dico_stat_session["max"] = max(Y_session)

print(dico_stat)
print(dico_stat_all)
print(dico_stat_session)

#dico_stat
txt_stat= ""
for stat, val in dico_stat.items():
    txt_stat+= stat + ": " + "{}".format(val) + "\n"

#dico_stat_all
txt_stat_all= ""
for stat, val in dico_stat_all.items():
    txt_stat_all+= stat + ": " + "{}".format(val) + "\n"

#dico_stat_session
txt_stat_session= ""
for stat, val in dico_stat_session.items():
    txt_stat_session+= stat + ": " + "{}".format(val) + "\n"


#plot

#annotate bars
def autolabel(rects, thres_annot, ax, tot_usage):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        if height > thres_annot:
            ax.text(rect.get_x() + rect.get_width()/2., 10+height,
                    "{}: {}-({:.2%})".format(int(rect.get_x()+rect.get_width()/2.), int(height), int(height)/tot_usage),
                ha='center', va='bottom')

print("plotting")

fig, ax = plt.subplots()

#width = 100
fill = ax.fill(X, Y_session, color='blue')
line2 = ax.plot(X, Y_all, color='green')
line1 = ax.plot(X, Y, color='red')

ax.set_title("Repartition of the TTL for unique ip per day")
ax.yaxis.grid(True, which='both')
ax.set_xlabel("TTL")
ax.set_ylabel("Usage")
ax.set_yscale("log")
ax.legend(['filter: not icmp', 'filter: not icmp and (port 23 or 2323)', 'filter: Logged session telnet'])

ax.set_yticks([10**x for x in range(9)])
ax.set_xticks([x for x in range(256) if x%5==0])
ax.set_xticklabels([x for x in range(256) if x%5==0], rotation=45)

#Add supposed OS version
fig.text(0.22, .73, "*nix (Linux/Unix)", bbox={'facecolor':'green', 'alpha':0.5, 'pad':10})
fig.text(0.40, .73, "Windows", bbox={'facecolor':'green', 'alpha':0.5, 'pad':10})
fig.text(0.73, .73, "Solaris/AIX", bbox={'facecolor':'green', 'alpha':0.5, 'pad':10})


plt.show()

