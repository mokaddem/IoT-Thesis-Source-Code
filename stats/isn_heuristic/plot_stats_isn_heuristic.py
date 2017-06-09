#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from pprint import pprint
from datetime import datetime
from datetime import timedelta
from matplotlib.dates import MONDAY
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
import matplotlib.pyplot as plt
import ast
import sys
from statistics import mean, median, pstdev, pvariance

#annotate curve
def autolabel2(ax, max_y, avg):
    """tot_number_of_session
    Attach a text label above each bar displaying its height
    """
    xy = ax.lines[0].get_xydata()
    for i, tab in enumerate(xy):
        x, y = tab
        if y not in [19224, 20601, 9545, 10549, 17111, 8445]:
        #if y < 7580:
            continue
        max_y_today = val_tot_sum[i]
        ax.text(x, y*0.01+y, 
                "{}\n{}-({:.2%})".format(dico_val_date[y].strftime("%d %b '%y"), int(y), y/max_y_today),
                ha='center', va='bottom')



with open("make_stats23_2323_sum.output", "r") as f:
    temp = f.read()

baseList = ast.literal_eval(temp)

l23 = baseList[0]
l2323 = baseList[1]
lsum = baseList[2]
ltotsum = baseList[3]
tot_ip = baseList[4]
dico_val_date = {}

date_23 = []
val_23 = []
date_2323 = []
val_2323 = []
date_sum = []
val_sum = []
date_tot_sum = []
val_tot_sum = []

for [d, v] in l23:
    d = str(d)
    cur_date = datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]))
    date_23.append(cur_date)
    val_23 += [v]
for [d, v] in l2323:
    d = str(d)
    date_2323.append(datetime(int(d[0:4]), int(d[4:6]), int(d[6:8])))
    val_2323 += [v]
for [d, v] in lsum:
    d = str(d)
    date_sum.append(datetime(int(d[0:4]), int(d[4:6]), int(d[6:8])))
    val_sum += [v]
    dico_val_date[v] = datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]))
for [d, v] in ltotsum:
    d = str(d)
    date_tot_sum.append(datetime(int(d[0:4]), int(d[4:6]), int(d[6:8])))
    val_tot_sum += [v]

fig, ax = plt.subplots()

ax.plot(date_sum, val_sum)
ax.plot(date_23, val_23)
ax.plot(date_2323, val_2323)

text_info = ""
text_info += "Total number of unique ip: {}".format(tot_ip)
fig.text(0.75, .75, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})



# every monday
mondays = WeekdayLocator(MONDAY)
months = MonthLocator(range(1, 13), bymonthday=1)
monthsFmt = DateFormatter("%d %b '%y")
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_major_formatter(monthsFmt)
ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()


plt.legend(['sum', 'tcp.dst = 23', 'tcp.dst = 2323'])
plt.ylabel("Unique IP where ISN = ip.dst")
plt.xlabel("Date")
plt.title("Unique IP addresses per day having tcp.isn == ip.dst over time")

autolabel2(ax, tot_ip, mean(val_sum))

plt.show()



