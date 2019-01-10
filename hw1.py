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

# 創建樹
def create_tree(all_items,items_dict):
    inittree = FP_Node('Null', None)
    inittree.num = 0
    # 存取每一筆購買的項目，並按照所有交易中，每個項目被購買的數量大小排序，由多至少
    items_sort = []
    # 為了要把每一筆購買的項目按照所有交易中，每個項目被購買的數量大小排序，由多至少
    for items in all_items:
        sort_all_items = {}
        for item in items:
            if item in items_dict:
                sort_all_items[item] = items_dict[item]
        has_sorted = [w[0] for w in sorted(sort_all_items.items(), key = lambda k: (k[1],k[0]),reverse = True)]
        if has_sorted != []:
            items_sort.append(has_sorted)
    
    for has_sorted in items_sort:
        pdict = {}
        update_tree(has_sorted,inittree,items_dict,pdict)
    return inittree

def update_tree(has_sorted,inittree,items_dict,pdict):
    # 如果每筆資料中，在所有交易中被購買最多的，沒有在父節點就要加進去樹中
    if has_sorted[0] not in inittree.child:
        inittree.child[has_sorted[0]] = FP_Node(has_sorted[0],inittree)
        pdict[inittree.child[has_sorted[0]].item] = 0
        for i in pdict:
            inittree.child[has_sorted[0]].parent_dict(i)
    # 如果每筆資料中，在所有交易中被購買最多的，有在父的節點就要 + num       
    else:
        inittree.child[has_sorted[0]].num += 1
        pdict[inittree.child[has_sorted[0]].item] = 0
    # 如果一筆交易中，有兩個以上的交易，就按照上述方法做
    if len(has_sorted) > 1:
        update_tree(has_sorted[1::],inittree.child[has_sorted[0]],items_dict,pdict)

def PowerSetsRecursive(items):
    result = [[]]
    for x in items:
        result.extend([subset + [x] for subset in result])
    return result

def dictset(items,i,pdict,val):
    list_set = []
    list_set.extend(i)
    itemdict = {}
    num = val
    for li in range(len(list_set)):
        if num > pdict[list_set[li]]:
            num = pdict[list_set[li]]
    list_set.append(items)
    itemdict[frozenset(list_set)] = num
    return itemdict

def mergedict(x,y):
    for key,val in y.items():
        if key in x.keys():
            x[key] += val
        else:
            x[key] = val
    return x
# 挖掘頻繁項目
def mine_tree(inittree,items_dict,num,number):
    itemsort = [w[0] for w in sorted(items_dict.items(), key = lambda k: (k[1],k[0]),reverse = True)]
    total = 0
    for item in itemsort:
        itemdict = {}
        plist = []
        plist = inittree.search(item,plist)
        for pdict in plist:
            if pdict != {}:
                val = pdict[item]
                pdict.pop(item)
                for i in PowerSetsRecursive(pdict.keys()):
                    itemdict = mergedict(itemdict,dictset(item,i,pdict,val))
        itemdict = {key:val for key,val in itemdict.items() if val >= num}
        for key,val in itemdict.items():
            print('%s %.5f' % (set(key),val/number*100))
            total += 1
    return total

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
    inittree = create_tree(all_items,items_dict)
    total = mine_tree(inittree,items_dict,min_sup*number,number)
    tEnd = time.time()#計時結束
    print ("花了 %f 秒" % (tEnd - tStart))
    print("有 %d 筆" % total)
    t1[i-1]=(tEnd - tStart)
    x1[i-1]= i * 2 + 3
plt.plot(x1,t1) 
plt.xlabel("min_sup(%)") 
plt.ylabel("time") 
plt.title("fp-growth") 
plt.show()

#print(inittree.print_tree())