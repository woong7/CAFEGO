import csv
import pandas as pd


with open('C:/Users/rjsdnd0316/Desktop/testpy/crawledminor.csv','r', encoding='utf-8') as f:
    dr = csv.DictReader(f)
    s = pd.DataFrame(dr)
    print(s)
    ss = []
    for i in range(len(s)):
        st = (s['stores'][i], s['X'][i], s['Y'][i],  s['road_address'][i])
        ss.append(st)

    print(ss)
#for i in range(len(s)):
    #(name=ss[i][0], location_x=ss[i][1], location_y=ss[i][2], address=ss[i][3])