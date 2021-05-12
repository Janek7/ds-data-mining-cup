#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 15:03:25 2021

@author: Moritz
"""


# for every itemID, a popularity score is calculated based on clicks, basket, and orders
# Additonally, the main topic and popularity rank for the main topic is added as an item attribute. 
# Look at data frame "df" for the popularity score, and the matrix "mat" for the co-occurences.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

path = "/media/Moritz/080FFDFF509A959E/BWsync_share/Master_BW/Data Mining Cup/code_and_data/"
items = pd.read_csv(path + "items.csv", sep = "|")
T = pd.read_csv(path + "transactions.csv", sep = "|")

#%%

#df = pd.DataFrame(columns = ["itemID", "clicks", "basket", "orders", "pop", "main topic", "rank_main_topic"])
tid = np.sort(T["itemID"].unique())

def length(x):
    if type(x) == str:
        return len(x)
    else:
        return None

def cut_main_topic(x): 
    # Most books have a main topic consisting of 2-4 characters, 
    # which is why the 5th or 6th chars are simply ignored.
    try:
        if len(x) > 4: 
            return x[0:4]
        else:
            return x
    except:
        pass

df = items.loc[items["itemID"].isin(tid)]    
df = df[["itemID", "main topic"]]
df["main topic"] = items.loc[items["itemID"].isin(tid)]["main topic"].apply(lambda x: cut_main_topic(x))

#%% 

# simple way, summing up all orders, basket addition and clicks
#df = df.merge(T.groupby("itemID").sum()[["click","basket","order"]], 
#         left_on = "itemID", right_on = "itemID", how = "inner")

# more realistic: In one session, only count the "most important" action: order > basket > click 
def metric(x):    
    if x[2] > 0:
        return [0,0,x[2]]
    elif x[1] > 0:
        return [0,x[1],0]
    else:
        return [x[0],0,0]
T_grouped = T.groupby(["itemID","sessionID"]).sum()  
m = T_grouped.apply(lambda x: metric(x), axis = 1).values
click = np.zeros((len(T),))
basket = np.zeros((len(T),))
order = np.zeros((len(T),))
for i in range(len(T)):
    click[i], basket[i], order[i] = m[i]

T_grouped["click"] = click
T_grouped["basket"] = basket
T_grouped["order"] = order
df = df.merge(T_grouped.groupby("itemID").sum(), left_on = "itemID", right_on = "itemID", how = "inner")

#%% popularity score
def pop(x, a, b, c):
    return a * x[0] + b * x[1] + c * x[2]

a = 1
b = 5 # maybe higher? almost like bought..
c = 10
df["pop"] = df[["click", "basket", "order"]].apply(lambda x: pop(x, a, b, c), axis = 1)

def rank_by_topic(x, df):
    return sum(df.loc[df["main topic"] == x[0]]["pop"] > x[1]) + 1
    
df["rank_main_topic"] = df[["main topic", "pop"]].apply(lambda x: rank_by_topic(x,df), axis = 1)




#%%

# most popular books:
    
print("Most popular books:")
print("")
best = df.sort_values(by = "pop", ascending = False)["itemID"].head()
print(items.loc[items["itemID"].isin(best)]["title"])

# most popular books in the categories ... 
best = df.loc[df["main topic"] == "FM"].sort_values(by = "pop", ascending = False)[["itemID", "pop", "order", "basket", "click"]].head()
best = best.merge(items.loc[items["itemID"].isin(best["itemID"])][["itemID","title"]], on = "itemID")

#%% co-occurence matrix
mat = np.zeros((len(tid), len(tid)), dtype = "int64")
T.groupby("sessionID").count()
for sid in T["sessionID"].unique():
    data = T[T["sessionID"] == sid]
    if len(data) > 1:
        for k in range(len(data)):
            for l in range(len(data)):
                mat[np.where(tid == data.iloc[k]["itemID"])[0][0]][np.where(tid == data.iloc[l]["itemID"])[0][0]] += 1
for i in range(len(tid)):
    mat[i][i] = 0



#%% illustration of co-occurence matrix 
np.where(mat == np.max(mat))
a = items[items["itemID"] == tid[725]]
b = items[items["itemID"] == tid[14744]]

n_occ = np.sum(mat, axis = 1)/2
np.max(n_occ)

plt.boxplot(n_occ)
sum(n_occ > 0) #14471 books co-occur with at least once with other book 






#TODO! Why are there odd rowsums?

#sum(mat[1])

#sids = T[T["itemID"] == 30277]["sessionID"].values

#T[T["sessionID"].isin(sids)]

# indexes for itemID 30277:
#sum((mat[np.where(tid == 30277)] > 0)[0])





