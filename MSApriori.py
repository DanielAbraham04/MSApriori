#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 19:05:36 2024

@author: danielabraham
"""

import os
import sys
import pandas as pd


data_file = sys.argv[1]
params_file = sys.argv[2]
lambda_value = sys.argv[3]
sdc_value = sys.argv[4]

def preprocessing(data_file):
    item_dictionary = {}
    c = 0
    with open(data_file, 'r') as file:
        for line in file:
            for i in line.strip().strip(',').split(','):
                if i not in item_dictionary.keys():
                    item_dictionary[i] = c
                    c += 1      
    return item_dictionary

def read_data_file(data_file,item_dictionary):
    transactions = []
    item_set = set()
    item_counts = {}
    with open(data_file, 'r') as file:
        for line in file:
            transaction = []
            line = line.replace('\ufeff', '')
            if line=='\n':
                continue
            for i in line.strip().strip(',').split(','):
                transaction.append(item_dictionary[i])
                item_set.add(item_dictionary[i])
                if item_dictionary[i] not in item_counts.keys():
                    item_counts[item_dictionary[i]] = 1
                else:
                    item_counts[item_dictionary[i]] += 1
            transactions.append(transaction)
    return transactions, item_set, item_counts

def MIS_file_creation(item_counts,n,params_file,lambda_value,sdc_value):
    mis_str=""
    support_list=[]
    for i,j in item_counts.items():
        sup=round(((j/n)*lambda_value),5)
        mis_temp_str = "MIS(" + str(i) + ") = " + str(sup) + "\n"
        support_list.append(sup)
        mis_str += mis_temp_str
    mis_temp_str = "SDC = " + str(sdc_value)
    mis_str += mis_temp_str
    if os.path.exists(params_file):
        os.remove(params_file)
    file = open(params_file, 'w')
    file.write(mis_str)
    file.close()
    return support_list
    
def read_parameter_file(parameter_file):
    mis = {}
    with open(parameter_file, 'r') as file:
        for line in file:
            if line.startswith('MIS'):
                item, value = line.strip().split(' = ')
                item = item.split('(')[1].split(')')[0]
                if str(item) != "rest":
                    item=int(item)
                mis[item] = float(value)
            elif line.startswith('SDC'):
                sdc = float(line.strip().split(' = ')[1])
    return mis, sdc

def init_pass(mis, item_set_sorted_mis, n, item_counts):
    l=[]
    min_mis=mis[item_set_sorted_mis[0]]
    for i in item_set_sorted_mis:
        if item_counts[i]/n >= min_mis:
            l.append(i)
    return l
        
def level2_candidate_gen(l, mis, sdc, item_counts, n):
    c2 = []
    for i in range(len(l)):
        if item_counts[l[i]]/n >= mis[l[i]]:
            for j in range(i+1, len(l)):
                if item_counts[l[j]]/n >= mis[l[i]] and abs(item_counts[l[j]]/n - item_counts[l[i]]/n) <= sdc:
                    c2.append([l[i], l[j]])
    return c2

def ms_candidate_gen(fk_minus_1, mis, sdc, item_counts, n):
    ck = []
    c=()
    for f1 in fk_minus_1:
        for f2 in fk_minus_1:
            f1, f2 = tuple(f1), tuple(f2)
            if f1[:-1] == f2[:-1] and f1[-1] < f2[-1] and abs(item_counts[f1[-1]]/n - item_counts[f2[-1]]/n) <= sdc:
                c = f1 + (f2[-1],)
                ck.append(c)
                subsets = [c[:i] + c[i+1:] for i in range(len(c))]
                #print(subsets)
                for s in subsets:
                    if (c[0] in s) or (mis[c[1]] == mis[c[0]]):
                        if tuple(s) not in fk_minus_1:
                            ck.remove(c)
                            break
    return ck

def calculate_support(itemset, transactions):
    count = sum(1 for transaction in transactions if set(itemset).issubset(transaction))
    return count


item_dictionary = preprocessing(data_file)
for i,j in item_dictionary.items():
    print("%s : %d" % (i,j))
    
transactions, item_set, item_counts = read_data_file(data_file,item_dictionary)

for i,j in item_counts.items():
    print("%d : %d" % (i,j) )
n=len(transactions)
print(n)
support_list = MIS_file_creation(item_counts,n,params_file,lambda_value,sdc_value)
support_df = pd.Series(support_list)
print(support_df.describe())
mis, sdc = read_parameter_file(params_file)
if "rest" in mis.keys():
    for item in item_set:
        if item not in mis.keys():
            mis[item]=mis["rest"]
    del mis["rest"]

sorted_mis = sorted(mis.items(), key=lambda x:x[1])
item_set_sorted_mis = []
for i in sorted_mis:
    item_set_sorted_mis.append(i[0])
l = init_pass(mis, item_set_sorted_mis, n, item_counts)
f = []
f1 = {}
for i in l:
    tuple_with_i = (i,)
    if item_counts[i]/n >= mis[i]:
        cc=item_counts[i]
        tc=n
        cl=[]
        cl.append(cc)
        cl.append(tc)
        f1[tuple_with_i]=cl
f.append(f1)

# Generating frequent itemsets of length 2
c2 = level2_candidate_gen(l, mis, sdc, item_counts, n)
print(len(c2))
f2 = {}
for c in c2:
    support_c = calculate_support(c, transactions) / n
    if support_c >= mis[min(c, key=lambda x: mis.get(x, 0))]:
        cc=calculate_support(c, transactions)
        tc=calculate_support(c[1:], transactions)
        cl=[]
        cl.append(cc)
        cl.append(tc)
        f2[tuple(c)] = cl
f.append(f2)

# Generating frequent itemsets of length k > 2
k = 2
while f[k-1]:
    ck = ms_candidate_gen(list(f[k-1].keys()), mis, sdc, item_counts, n)
    print(len(ck))
    fk = {}
    for c in ck:
        support_c = calculate_support(c, transactions) / n
        if support_c >= mis[min(c, key=lambda x: mis.get(x, 0))]:
            cc=calculate_support(c, transactions)
            tc=calculate_support(c[1:], transactions)
            cl=[]
            cl.append(cc)
            cl.append(tc)
            fk[tuple(c)] = cl
    f.append(fk)
    k += 1
sn=1
output=""
while sn < len(f):
    output+="(Length-"
    output+=str(sn)
    output+=" "
    output+=str(len(f[sn-1]))
    output+="\n"
    for x,y in f[sn-1].items():
        output+="("
        it=0
        while it < len(x)-1:
            output+=str(x[it])
            output+=" "
            it+=1
        output+=str(x[it])
        output+=") : "
        output+=str(y[0])
        output+=" : "
        output+=str(y[1])
        output+="\n"
    output+=")\n"
    sn+=1
print(output)

