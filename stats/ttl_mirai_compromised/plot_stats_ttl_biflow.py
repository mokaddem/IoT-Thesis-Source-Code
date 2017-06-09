#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.unicode'] = True
import ast
import sys
from pprint import pprint
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG
thres_annot = 50000

#with open("make_stats_ttl_biflow_port23_2323_windows.output", "r") as f:
with open("make_stats_ttl_biflow.output", "r") as f:
    temp = f.read()

baseArray = ast.literal_eval(temp)
baseArray23 = baseArray[0]
baseArray2323 = baseArray[1]
baseArraySession = baseArray[2]

dico_delta_ttl_23_6h = baseArray23[0]
dico_delta_ttl_23_24h = baseArray23[1]
dico_delta_ttl_23_10s = baseArray23[2]
tot_num_23 = baseArray23[3]

dico_delta_ttl_2323_6h = baseArray2323[0]
dico_delta_ttl_2323_24h = baseArray2323[1]
dico_delta_ttl_2323_10s = baseArray2323[2]
tot_num_2323 = baseArray2323[3]

dico_delta_ttl_session_6h = baseArraySession[0]
dico_delta_ttl_session_24h = baseArraySession[1]
dico_delta_ttl_session_10s = baseArraySession[2]

#PORT 23
# 6h -> port 23 and 2323 and not icmp
delta_ttl_23 = []
tot_sum_23 = 0
for ttl, val in dico_delta_ttl_23_6h.items():
    delta_ttl_23.append([ttl, val])
    tot_sum_23 += val
delta_ttl_23.sort(key=lambda x: int(x[0]))

x_23 = []
y_23 = []
for tab in delta_ttl_23:
    x_23.append(tab[0])
    y_23.append(tab[1])

# 24h -> port 23 and not icmp
delta_ttl_23_24 = []
for ttl, val in dico_delta_ttl_23_24h.items():
    delta_ttl_23_24.append([ttl, val])
delta_ttl_23_24.sort(key=lambda x: int(x[0]))

y_23_24 = []
for tab in delta_ttl_23_24:
    y_23_24.append(tab[1])

# 10s -> port 23 and not icmp
delta_ttl_23_10s = []
for ttl, val in dico_delta_ttl_23_10s.items():
    delta_ttl_23_10s.append([ttl, val])
delta_ttl_23_10s.sort(key=lambda x: int(x[0]))

y_23_10s = []
for tab in delta_ttl_23_10s:
    y_23_10s.append(tab[1])

X_23 = np.array(x_23)
Y_23 = np.array(y_23)
Y_23_24 = np.array(y_23_24)
Y_23_10s = np.array(y_23_10s)

# ttl delta at particular point
arr_txt_val_23 = []
for n in [2, 64, 128, 191]:
    txt_values_23 = r"\setlength{\parindent}{0mm}"
    for i in range(-2+n, 2+n):
        val = dico_delta_ttl_23_6h[i]
        txt_values_23 += r" $ \Delta_{ttl = " + str(i) + r"} = "\
                + r"{:.4}".format(val/tot_sum_23*100)  + r"\% "\
                + r" \; (" + str(val) + r") $ \\"
    arr_txt_val_23.append(txt_values_23)



#PORT 2323
# 6h -> port 2323 and not icmp
delta_ttl_2323 = []
tot_sum_2323 = 0
for ttl, val in dico_delta_ttl_2323_6h.items():
    delta_ttl_2323.append([ttl, val])
    tot_sum_2323 += val
delta_ttl_2323.sort(key=lambda x: int(x[0]))

x_2323 = []
y_2323 = []
for tab in delta_ttl_2323:
    x_2323.append(tab[0])
    y_2323.append(tab[1])

# 24h -> port 2323 and not icmp
delta_ttl_2323_24 = []
for ttl, val in dico_delta_ttl_2323_24h.items():
    delta_ttl_2323_24.append([ttl, val])
delta_ttl_2323_24.sort(key=lambda x: int(x[0]))

y_2323_24 = []
for tab in delta_ttl_2323_24:
    y_2323_24.append(tab[1])

# 10s -> port 2323 and not icmp
delta_ttl_2323_10s = []
for ttl, val in dico_delta_ttl_2323_10s.items():
    delta_ttl_2323_10s.append([ttl, val])
delta_ttl_2323_10s.sort(key=lambda x: int(x[0]))

y_2323_10s = []
for tab in delta_ttl_2323_10s:
    y_2323_10s.append(tab[1])

X_2323 = np.array(x_2323)
Y_2323 = np.array(y_2323)
Y_2323_24 = np.array(y_2323_24)
Y_2323_10s = np.array(y_2323_10s)


# ttl delta at particular point
arr_txt_val_2323 = []
for n in [2, 64, 128, 191]:
    txt_values_2323 = r"\setlength{\parindent}{0mm}"
    for i in range(-2+n, 2+n):
        val = dico_delta_ttl_2323_6h[i]
        txt_values_2323 += r" $ \Delta_{ttl = " + str(i) + r"} = "\
                + r"{:.4}".format(val/tot_sum_2323*100)  + r"\% "\
                + r" \; (" + str(val) + r") $ \\"
    arr_txt_val_2323.append(txt_values_2323)


#SESSION ONLY
# 6h -> session
delta_ttl_session = []
tot_sum_session = 0
for ttl, val in dico_delta_ttl_session_6h.items():
    delta_ttl_session.append([ttl, val])
    tot_sum_session += val
delta_ttl_session.sort(key=lambda x: int(x[0]))

x_session = []
y_session = []
for tab in delta_ttl_23:
    x_session.append(tab[0])
    y_session.append(tab[1])

# 24h -> session
delta_ttl_session_24 = []
for ttl, val in dico_delta_ttl_session_24h.items():
    delta_ttl_session_24.append([ttl, val])
delta_ttl_session_24.sort(key=lambda x: int(x[0]))

y_session_24 = []
for tab in delta_ttl_session_24:
    y_session_24.append(tab[1])

# 10s -> session
delta_ttl_session_10s = []
for ttl, val in dico_delta_ttl_session_10s.items():
    delta_ttl_session_10s.append([ttl, val])
delta_ttl_session_10s.sort(key=lambda x: int(x[0]))

y_session_10s = []
for tab in delta_ttl_session_10s:
    y_session_10s.append(tab[1])

X_session = np.array(x_session)
Y_session_10s = np.array(y_session_10s)
Y_session = np.array(y_session) - Y_session_10s
Y_session_24 = np.array(y_session_24) - Y_session

# ttl delta at particular point
arr_txt_val_session = []
for n in [2, 64, 128, 191]:
    txt_values_session = r"\setlength{\parindent}{0mm}"
    for i in range(-2+n, 2+n):
        val = dico_delta_ttl_session_6h[i]
        txt_values_session += r" $ \Delta_{ttl = " + str(i) + r"} = "\
                + r"{:.4}".format(val/tot_sum_session*100)  + r"\% "\
                + r" \; (" + str(val) + r") $ \\"
    arr_txt_val_session.append(txt_values_session)


#PLOT

#annotate bars
def autolabel(rects, ax, tot_usage):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        x = rect.get_x() + rect.get_width()/2.
        if x in [0, 64, 127, 191]:
            ax.text(rect.get_x() + rect.get_width()/2., 10+height,
                    "{}: {}-({:.2%})".format(int(rect.get_x()+rect.get_width()/2.), int(height), int(height)/tot_usage),
                ha='center', va='bottom')

print("plotting")

fig, (ax_23, ax_2323, ax_session) = plt.subplots(nrows=3, ncols=1)

#width = 100
bars23_10 = ax_23.bar(X_23, Y_23_10s, align='center', color='green')
bars23_6 = ax_23.bar(X_23, Y_23, align='center', color='blue', bottom=Y_23_10s)
bars23_24 = ax_23.bar(X_23, Y_23_24, align='center', color='red', bottom=Y_23)
bars2323_10 = ax_2323.bar(X_2323, Y_2323_10s, align='center', color='green')
bars2323_6 = ax_2323.bar(X_2323, Y_2323, align='center', color='blue', bottom=Y_2323_10s)
bars2323_24 = ax_2323.bar(X_2323, Y_2323_24, align='center', color='red', bottom=Y_2323)
barsSess_10 = ax_session.bar(X_session, Y_session_10s, align='center', color='green')
barsSess_6 = ax_session.bar(X_session, Y_session, align='center', color='blue', bottom=Y_session_10s)
barsSess_24 = ax_session.bar(X_session, Y_session_24, align='center', color='red', bottom=Y_session)
#line3 = ax.plot(X_2323, Y_2323_10s, color='green', linewidth=2)
#line1 = ax.plot(X_2323, Y_2323, color='blue')
#line2 = ax.plot(X_2323, Y_2323_24, color='red', linewidth=2)

fig.suptitle("Delta of TTLs between the same reconnecting IP on the blackhole, for different filters and different time window", fontsize=14, fontweight='bold')
ax_23.set_title("Port 23")
ax_2323.set_title("Port 2323")
ax_session.set_title("Logged telnet session")
ax_23.yaxis.grid(True, which='both')
ax_2323.yaxis.grid(True, which='both')
ax_session.yaxis.grid(True, which='both')
ax_23.set_xlabel("TTL delta")
ax_2323.set_xlabel("TTL delta")
ax_session.set_xlabel("TTL delta")
ax_23.set_ylabel("Occurences")
ax_2323.set_ylabel("Occurences")
ax_session.set_ylabel("Occurences")
ax_23.set_yscale("log")
ax_2323.set_yscale("log")
ax_session.set_yscale("log")
ax_23.legend(['window: 10s',
    'window: 6h', 
    'window: 24h'
    ])
ax_2323.legend(['window: 10s',
    'window: 6h', 
    'window: 24h'
    ])
ax_session.legend(['window: 10s',
    'window: 6h', 
    'window: 24h'
    ])

ax_23.set_yticks([10**x for x in range(9)])
ax_2323.set_yticks([10**x for x in range(9)])
ax_session.set_yticks([10**x for x in range(9)])
ax_23.set_xticks([x for x in range(211) if x%5==0])
ax_2323.set_xticks([x for x in range(211) if x%5==0])
ax_session.set_xticks([x for x in range(211) if x%5==0])
ax_23.set_xticklabels([x for x in range(211) if x%5==0], rotation=45)
ax_2323.set_xticklabels([x for x in range(211) if x%5==0], rotation=45)
ax_session.set_xticklabels([x for x in range(211) if x%5==0], rotation=45)
ax_23.set_xlim([-5, 210])
ax_2323.set_xlim([-5, 210])
ax_session.set_xlim([-5, 210])

#autolabel(bars3, ax, tot_num)

for i, txt_values in enumerate(arr_txt_val_23):
    fig.text(.20+i*0.15, .78, txt_values, bbox={'facecolor':'lightblue', 'alpha':1.0, 'pad':10}, fontsize=16)
for i, txt_values in enumerate(arr_txt_val_2323):
    fig.text(.20+i*0.15, .50, txt_values, bbox={'facecolor':'lightblue', 'alpha':1.0, 'pad':10}, fontsize=16)
for i, txt_values in enumerate(arr_txt_val_session):
    fig.text(.20+i*0.15, .21, txt_values, bbox={'facecolor':'lightblue', 'alpha':1.0, 'pad':10}, fontsize=16)

plt.show()

