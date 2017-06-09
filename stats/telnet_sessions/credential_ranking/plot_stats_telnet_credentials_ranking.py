#!/usr/bin/env python3.5
# -*-coding:UTF-8 -*

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import ast
import sys
import numpy as np
from statistics import mean, median, pstdev, pvariance

# CONFIG #
dataset = "blackhole27"
thres_om = 200

with open("make_stats_telnet_credentials_ranking.output", "r") as f:
    temp = f.read()

x = []
y = []
y_uniq = []
array_label = []
iteration = 0

dico = ast.literal_eval(temp)
# ranking := ((user, pass), occ)
ranking = ast.literal_eval(dico['ranking'])
ranking_uniq_array = ast.literal_eval(dico['ranking_uniq'])
session_without_cred = int(dico['session_without_cred'])
tot_number_of_session = int(dico['tot_number_of_session'])
echo_session = int(dico['echo_session'])
noecho_session = int(dico['noecho_session'])

sum_prob = session_without_cred

ranking_uniq = {}
for tup in ranking_uniq_array:
    cred, occ = tup
    cred = (cred[0]+b':'+cred[1]).decode('ascii', 'backslashreplace')
    ranking_uniq[cred] = occ

session_with_cred = 0
not_shown = 0
not_shown_occ = 0
sum_showed = 0
for cred, occ in ranking:
    if occ > thres_om:
        cred = (cred[0]+b':'+cred[1]).decode('ascii', 'backslashreplace')
        array_label.append(cred)
        x.append(iteration)
        y.append(occ)
        y_uniq.append(ranking_uniq[cred])
        sum_showed += occ
        iteration += 1
    else:
        not_shown += 1
        not_shown_occ += occ
    session_with_cred += occ

text_info = "SESSION:\n"
text_info += "Total number of session: {}\n".format(tot_number_of_session)
text_info += "Number of session with credential: {} ({:.2%})\n".format(session_with_cred, session_with_cred/tot_number_of_session)
text_info += "Session without credential or malformed: {} ({:.2%})\n".format(session_without_cred, session_without_cred/tot_number_of_session)
text_info += "Shown: {} ({:.2%})\n".format(sum_showed, sum_showed/session_with_cred)
text_info += "Not shown: {} ({:.2%})\n".format(not_shown, not_shown_occ/session_with_cred)
text_info += "\n"
text_info += "ECHO:\n"
text_info += "Session with ECHO option enabled: {} ({:.2%})\n".format(echo_session, echo_session/tot_number_of_session)
text_info += "Session with ECHO option not enabled: {} ({:.2%})\n".format(noecho_session, noecho_session/tot_number_of_session)


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
        ax.text(width*1.25, value+rect.get_height(), 
                "{} - {:.2%}".format(int(width), float(width)/float(session_with_cred)),
                ha='center', va='bottom')

print("plotting")

fig, ax = plt.subplots()

y_pos = np.arange(len(array_label))

bars = ax.barh(y_pos, y, align='center', color='g')
bars_uniq = ax.barh(y_pos, y_uniq, align='center', color='b')
ax.set_yticks(y_pos)
ax.set_yticklabels(array_label)
ax.invert_yaxis()


ax.set_xscale("log")
ax.xaxis.grid(True, which='both')

ax.set_ylabel("Credential used")
ax.set_xlabel("Occurences")
ax.set_title("Distribution of the credential used during a telnet session (filtered: <"+str(thres_om)+")")

fig.text(.65, .4, text_info, bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':10})
autolabel(bars, ax)

plt.legend(['Occurences', 'Occurences by unique IP'], loc='lower right')

plt.show()

