import numpy as np
import linecache
from collections import defaultdict
from collections import Counter
import matplotlib.pyplot as plt
import itertools
import csv
import time

class FP_Node:
    def __init__(self, item, parent):
        self.item = item  
        self.num = 1 
        self.parent = parent
        self.child = {}
        self.dict = {}

    def print_tree(self,i=4):
        print(' '*i,self.item,' ',self.num,' ',self.dict)
        for child in self.child.values():
            child.print_tree(i+4)

    def parent_dict(self,parent):
        self.dict[parent] = 0

    def merge_dict(self,x,y):
        for key,val in y.items():
            if key in x.keys():
                x[key] += val
            else:
                x[key] = val
        return x

    def add_num(self):
        for i in self.dict:
            self.dict[i]=self.num

    def search(self,item,plist):
        if self.item == item:
            self.add_num()
            plist.append(self.dict)
            return plist
        for child in self.child.values():
            child.search(item,plist)
        return plist
# 讀取檔案，每一筆交易中買了甚麼項目
def load(filename,num):
    text = []
    i = 0
    with open(filename,'r') as f:
        for line in f.readlines():
            if i < num:
                text.append([])
            items = line.split()
            text[int(items[1])-1].append(items[2])
            i += 1
    return text,num
# 讀取檔案，每一筆交易中買了甚麼項目
def load_csv(filename,num):
    text = []
    first = 0
    i = 0
    with open(filename,'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if first == 0:
                first = 1
            else:
                if i < num:
                    text.append([])
                items = line.split(',')
                if items[3] != 'NONE':
                    text[int(items[2])-1].append(items[3])
                i += 1
    return text,num
# 讀取檔案，每一筆交易中買了甚麼項目
def load_cho_csv(filename,num):
    text = []
    first = 0
    i = 0
    with open(filename,'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if first < 1:
                first = 1
            else:
                if i < num:
                    text.append([])
                items = line.split(',')
                text[int(items[0])-1].append('Survived_'+items[1])
                text[int(items[0])-1].append('Pclass_'+items[2])
                text[int(items[0])-1].append(items[5])
                if items[6] != '':
                    if float(items[6]) <= 10.0:
                        text[int(items[0])-1].append('Age(0-10)')
                    elif float(items[6]) > 10.0 and float(items[6]) <= 20.0:
                        text[int(items[0])-1].append('Age(10-20)')
                    elif float(items[6]) > 20.0 and float(items[6]) <= 40.0:
                        text[int(items[0])-1].append('Age(21-40)')
                    elif float(items[6]) > 40.0 and float(items[6]) <= 65.0:
                        text[int(items[0])-1].append('Age(41-65)')
                    else:
                        text[int(items[0])-1].append('Age(66-)')
                text[int(items[0])-1].append('Embarked_'+items[12])
                i += 1
    return text,num

def outputfile(all_items):
    with open('outputtitanic.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for i in all_items:
            writer.writerow(i)
# 計算所有交易中，每個項目被購買多少次
def caculate_item(all_items,min):
    items_dict = defaultdict(lambda: 0)
    for items in all_items:
        for item in items:
            items_dict[item] += 1
    items_dict = {key:val for key,val in items_dict.items() if val >= min}
    return items_dict

def create_l1(items_dict,level):
    l_list = []
    for key,val in items_dict.items():
        l_list.append(key)
    l_list = list(itertools.combinations(l_list,level))
    return l_list

def create_l2(items_dict,delete_list,level):
    end = 0
    l_list = []
    for key,val in items_dict.items():
        for i in key:
            if i not in l_list:
                l_list.append(i)
    l_list = list(itertools.combinations(l_list,level))
    l_list2=[]
    for it in l_list:
        it_list = []
        for i in it:
            it_list.append(i)
        it_set = set(it_list)
        num = 0
        for dit in delete_list:
            set_dit = set(dit)
            if set_dit.issubset(it_set):
                num = 1
        if num == 0:
            l_list2.append(it)
    if len(l_list2)==0:
        end = 1
    return l_list2,end,items_dict

def caculate_l1(all_items,items_dict,l_list,min_):
    end = 0
    element_dict = defaultdict(lambda: 0)
    delete_list = []
    for it in l_list:
        it_list = []
        for i in it:
            it_list.append(i)
        it_set = set(it_list)
        num = 0
        for items in all_items:
            set_items = set(items)
            if it_set.issubset(set_items):
                num += 1
        if num >= min_:
             element_dict[it] = num
        else:
           delete_list.append(it_list) 
    if len(element_dict.keys())==0:
        end = 1
        element_dict = items_dict
    return element_dict, delete_list, end
            
def caculate_l2(all_items,items_dict,l_list,min_):
    end = 0
    element_dict = defaultdict(lambda: 0)
    delete_list = []
    for it in l_list:
        it_list = []
        for i in it:
            it_list.append(i)
        it_set = set(it_list)
        num = 0
        for items in all_items:
            set_items = set(items)
            if it_set.issubset(set_items):
                num += 1
        if num >= min_:
             element_dict[it] = num
        else:
           delete_list.append(it_list) 
    if len(element_dict.keys())==0:
        end = 1
        element_dict = items_dict
    return element_dict, delete_list, end

def PowerSetsRecursive(items):
    result = [[]]
    for x in items:
        result.extend([subset + [x] for subset in result])
    return result

all_items,number = load("IBM-Quest-Data-Generator.exe/data.ntrans_0.1.nitems_0.1.1",99)
#all_items,number = load("IBM-Quest-Data-Generator.exe/data.ntrans_0.1.nitems_1",99)
#all_items,number = load("IBM-Quest-Data-Generator.exe/data.ntrans_1.nitems_0.1.1",984)
#all_items,number = load("IBM-Quest-Data-Generator.exe/data.ntrans_1.nitems_1",977)
#all_items,number = load_csv("transactions-from-a-bakery/BreadBasket_DMS.csv",9684)
#all_items,number = load_cho_csv("titanic/train.csv",891)
#outputfile(all_items)
t1 = np.zeros(10)
x1 = np.zeros(10)
for i in range(1,11):
    min_sup = i*0.02 + 0.03
    print("min_sup",min_sup)
    tStart = time.time()
    items_dict = caculate_item(all_items,min_sup*number)
    level_list=[]
    level_list.append(items_dict)
    l_ = create_l1(items_dict,2)
    items_dict,delete_list,end = caculate_l1(all_items,items_dict,l_,min_sup*number)
    level = 3
    if(end==0):
        level_list.append(items_dict)
    while(end==0):
        l_,end,items_dict = create_l2(items_dict,delete_list,level)
        if end == 0:
            items_dict,delete_list,end = caculate_l2(all_items,items_dict,l_,min_sup*number)
        level += 1
        if end == 0:
            level_list.append(items_dict)
    tEnd = time.time()#計時結束
    for a in range(len(level_list)):
        print(a+1,": ",len(level_list[a]))
    print('items_dict',level_list)
    print ("花了 %f 秒" % (tEnd - tStart))
    #print("有 %d 筆" % total)
    t1[i-1]=(tEnd - tStart)
    x1[i-1]= i * 2 + 3
plt.plot(x1,t1) 
plt.xlabel("min_sup(%)") 
plt.ylabel("time") 
plt.title("apriori") 
plt.show()

#print(inittree.print_tree())