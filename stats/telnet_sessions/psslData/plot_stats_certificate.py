#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
import ast, json
import sys
import numpy as np
import math
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"

def getCountryCode():
    with open('countryCode.txt', 'r') as f:
        temp = f.read()

    temp = temp.splitlines()
    dico_countryCode = {}
    for line in temp:
        arr = line.split('\t')
        dico_countryCode[arr[1].strip(' ')] = arr[0].strip(' ')
    return dico_countryCode


with open("make_stats_certificate.output", "r") as f:
    theJson = json.load(f)


dico_country = theJson['country']
dico_organization = theJson['org']
dico_organizationalUnit = theJson['orgUnit']
totCert = theJson['totCert']
totIp = theJson['totIp']
totIpCert = theJson['totIpCert']
totIpNoCert = totIp - totIpCert
countryCodeDico = getCountryCode()

###
#merge uppercase and lower case
dico_country_merged = {}
to_process = []
for item, occ in dico_country.items():
    if item != item.upper():
        to_process += [(item, occ)]
    else:
        dico_country_merged[item] = occ
for item, occ in to_process:
    if item.upper() in dico_country_merged:
        dico_country_merged[item.upper()] += occ
    else:
        dico_country_merged[item] = occ

TOPLOT = dico_country_merged
TOPLOT_TEXT = "Country"
thres_om = 1
LEFT = 0.30
###

x = []
y = []
array_label = []
iteration = 0

# ranking := ((user, pass), occ)


list_tup = []
list_tup_to_write = []
for item, occ in TOPLOT.items():
    list_tup.append([item, occ])
    list_tup_to_write.append([item, occ, "{:.2%}".format(float(occ)/float(totCert)), math.log(occ)])
list_tup.sort(key=lambda x: x[1], reverse=True)
list_tup_to_write.sort(key=lambda x: x[1], reverse=True)

with open('plotted_data.json', 'w') as f:
    json.dump(list_tup_to_write, f)


not_shown = 0
not_shown_occ = 0
sum_showed = 0
for item, occ in list_tup:
    if occ > thres_om:
        try:
            CD = countryCodeDico[item]
            array_label.append(item + ': ' + CD)
        except KeyError:
            array_label.append(item)
        x.append(iteration)
        y.append(occ)
        sum_showed += occ
        iteration += 1
    else:
        not_shown += 1
        not_shown_occ += occ

text_info = ""
text_info += "Number of processed ip: {}\n".format(totIp)
text_info += "Number of certificate collected: {}\n".format(totCert)
text_info += "Number of ip with certificate: {} ({:.2%})\n".format(totIpCert, totIpCert / totIp)
text_info += "Number of ip without certificate: {} ({:.2%})\n".format(totIpNoCert, totIpNoCert / totIp)


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
        ax.text(width*1.65, value+0.5*rect.get_height(), 
                "{} - {:.2%}".format(int(width), float(width)/float(totCert)),
                ha='center', va='bottom')

print("plotting")

fig, ax = plt.subplots(gridspec_kw = {'left':LEFT, 'top':0.95})

y_pos = np.arange(len(array_label))

bars = ax.barh(y_pos, y, align='center', color='gb')
ax.set_yticks(y_pos)
ax.set_yticklabels(array_label)
ax.invert_yaxis()


ax.set_xscale("log")
ax.xaxis.grid(True, which='both')

ax.set_ylabel(TOPLOT_TEXT)
ax.set_xlabel("Occurences")
ax.set_title("Distribution of "+TOPLOT_TEXT+" collected in certificate, only for telnet session with at least 2 commands sent (filtered: <"+str(thres_om)+")")

fig.text(.65, .2, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})
autolabel(bars, ax)

plt.show()

