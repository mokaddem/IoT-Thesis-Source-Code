#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import ast
import sys
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG
thres_om_src = 200
thres_annot_src = 1700
thres_om_dst = 1
thres_annot_dst = 1

with open("make_stats_port_repartition.output", "r") as f:
    temp = f.read()

baselist = ast.literal_eval(temp)
dico_src = baselist[0]
dico_dst = baselist[1]

combi_src = []
for port, val in dico_src.items():
    combi_src.append([port, val])
combi_src.sort(key=lambda x: int(x[0]))

combi_dst = []
for port, val in dico_dst.items():
    combi_dst.append([port, val])
combi_dst.sort(key=lambda x: int(x[0]))


y_src = []
x_src = []
omitted_src = 0
tot_src = 0
for tab in combi_src:
    tot_src += tab[1]
    if tab[1] > thres_om_src:
        x_src.append(tab[0])
        y_src.append(tab[1])
    else:
        omitted_src += tab[1]

X_src = np.array(x_src)
Y_src = np.array(y_src)

y_dst = []
x_dst = []
omitted_dst = 0
tot_dst = 0
for tab in combi_dst:
    tot_dst += tab[1]
    if tab[1] > thres_om_dst:
        x_dst.append(tab[0])
        y_dst.append(tab[1])
    else:
        omitted_dst += tab[1]

X_dst = np.array(x_dst)
Y_dst = np.array(y_dst)

#stat src
dico_stat_src = {}
dico_stat_src["mean"] = mean(Y_src)
dico_stat_src["median"] = median(Y_src)
dico_stat_src["std_dev"] = pstdev(Y_src)
dico_stat_src["variance"] = pvariance(Y_src)
dico_stat_src["max"] = max(Y_src)
dico_stat_src["showed"] = len(Y_src)
dico_stat_src["omitted"] = omitted_src
dico_stat_src["total"] = tot_src

dico_port_src = {}
dico_port_src["port_23"] = dico_src[23]
dico_port_src["port_2323"] = dico_src[2323]
dico_port_src["port_80"] = dico_src[80]
dico_port_src["port_443"] = dico_src[443]
dico_port_src["port_7"] = dico_src[7]
dico_port_src["port_22"] = dico_src[22]
#stat dst
dico_stat_dst= {}
dico_stat_dst["mean"] = mean(Y_dst)
dico_stat_dst["median"] = median(Y_dst)
dico_stat_dst["std_dev"] = pstdev(Y_dst)
dico_stat_dst["variance"] = pvariance(Y_dst)
dico_stat_dst["max"] = max(Y_dst)
dico_stat_dst["showed"] = len(Y_dst)
dico_stat_dst["omitted"] = omitted_dst
dico_stat_dst["total"] = tot_dst

dico_port_dst = {}
dico_port_dst["port_23"] = dico_dst[23]
dico_port_dst["port_2323"] = dico_dst[2323]
dico_port_dst["port_80"] = dico_dst[80]
dico_port_dst["port_443"] = dico_dst[443]
dico_port_dst["port_7"] = dico_dst[7]
dico_port_dst["port_22"] = dico_dst[22]


print(dico_stat_src)
print(dico_stat_dst)

#src
txt_stat_src = ""
for stat, val in dico_stat_src.items():
    txt_stat_src += stat + ": " + "{}".format(val) + "\n"

list_port_src = []
for port, val in dico_port_src.items():
    list_port_src.append([port, val])
list_port_src.sort(key=lambda x: int(x[1]))
    
txt_port_src = ""
for tab in list_port_src:
    port = tab[0]
    val = tab[1]
    txt_port_src += port + ": " + "{}".format(val) + "\n"
text_info_src = txt_stat_src + "--------------------------\n"+txt_port_src
#dst
txt_stat_dst = ""
for stat, val in dico_stat_dst.items():
    txt_stat_dst += stat + ": " + "{}".format(val) + "\n"

list_port_dst = []
for port, val in dico_port_dst.items():
    list_port_dst.append([port, val])
list_port_dst.sort(key=lambda x: int(x[1]))
    
txt_port_dst = ""
for tab in list_port_dst:
    port = tab[0]
    val = tab[1]
    txt_port_dst += port + ": " + "{}".format(val) + "\n"
text_info_dst = txt_stat_dst + "--------------------------\n"+txt_port_dst


#plot

#annotate bars
def autolabel(rects, thres_annot, ax, tot_usage):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        if height > thres_annot:
            if height in [1907, 2673]:
                continue
            ax.text(rect.get_x() + rect.get_width()/2., 10+height,
                    "{}: {}-({:.2%})".format(int(rect.get_x()+rect.get_width()/2.), int(height), int(height)/tot_usage),
                ha='center', va='bottom')

print("plotting")

fig, (ax_src, ax_dst) = plt.subplots(nrows=2, ncols=1)

width = 100
bars_src = ax_src.bar(X_src, Y_src, width, align='center')
bars_dst = ax_dst.bar(X_dst, Y_dst, width, align='center')

autolabel(bars_src, thres_annot_src, ax_src, tot_src)
autolabel(bars_dst, thres_annot_dst, ax_dst, tot_dst)

ax_src.set_title("Repartition of the port usage for Mirai compromised devices (filtered: <"+str(thres_om_src)+")")
ax_dst.set_title("Repartition of the port usage for Mirai compromised devices (filtered: <"+str(thres_om_dst)+")", )
ax_src.set_xlabel("Source port")
ax_src.set_ylabel("Usage")
ax_src.set_yscale("log")

ax_dst.set_xlabel("Destination port")
ax_dst.set_ylabel("Usage")
ax_dst.set_yscale("log")
fig.text(.87, .73, text_info_src, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})
fig.text(.87, .23, text_info_dst, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})

plt.show()

