import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import MiniMap
import requests
import folium
import collections

def whole_region(keyword, start_x, start_y, end_x, end_y):
    page_num=1
    all_data_list=[]

    while(1):
        url='https://dapi.kakao.com/v2/local/search/keyword.json'
        params={'query':keyword, 'page':page_num, 'rect': f'{start_x},{start_y},{end_x},{end_y}'}
        headers={'Authorization': 'KakaoAK 8a39917a1ea51c15d8c0d936782abf3a'}
        resp=requests.get(url, params=params, headers=headers)

        search_count=resp.json()['meta']['total_count']
       # print('총 개수', search_count)

        if search_count>45:
            #print('좌표 4등분')
            dividing_x = (start_x+end_x)/2
            dividing_y = (start_y+end_y)/2

            all_data_list.extend(whole_region(keyword,start_x, start_y, dividing_x, dividing_y))
            all_data_list.extend(whole_region(keyword,dividing_x, start_y, end_x, dividing_y))
            all_data_list.extend(whole_region(keyword,start_x, dividing_y, dividing_x, end_y))
            all_data_list.extend(whole_region(keyword,dividing_x, dividing_y, end_x, end_y))
            return all_data_list

        else:
            if resp.json()['meta']['is_end']:
                all_data_list.extend(resp.json()['documents'])
                return all_data_list
            else:
                #print('다음페이지')
                page_num +=1
                all_data_list.extend(resp.json()['documents'])

def overlapped_data(keyword, start_x, start_y, next_x, next_y, num_x, num_y):
    overlapped_result=[]

    for i in range(1, num_x+1):
        end_x=start_x+next_x
        initial_start_y=start_y
        for j in range(1, num_y+1):
            print(i,j)
            end_y = initial_start_y+next_y
            each_result=whole_region(keyword, start_x, initial_start_y, end_x, end_y)
            overlapped_result.extend(each_result)
            initial_start_y=end_y
        start_x=end_x

    return overlapped_result


def make_map(dfs):
    m=folium.Map(location=[37.566826, 126.9786567], zoom_start=12)

    minimap=MiniMap()
    m.add_child(minimap)

    for i in range(len(dfs)):
        folium.Marker([df['Y'][i], df['X'][i]], tooltip=dfs['stores'][i], popup=dfs['place_url'][i]).add_to(m)
    return m


keyword='카페'
start_x=126.75
start_y=37.43
next_x=0.01
next_y=0.01
num_x=44
num_y=28


overlapped_result= overlapped_data(keyword, start_x, start_y, next_x, next_y, num_x, num_y)

results=list(map(dict, collections.OrderedDict.fromkeys(tuple(sorted(d.items())) for d in overlapped_result)))
X=[]
Y=[]
stores=[]
road_address=[]
place_url=[]
ID=[]

for place in results:
    X.append(float(place['x']))
    Y.append(float(place['y']))
    stores.append(place['place_name'])
    road_address.append(place['road_address_name'])
    place_url.append(place['place_url'])
    ID.append(place['id'])

    ar=np.array([ID, stores, X, Y, road_address, place_url]).T
    df=pd.DataFrame(ar, columns = ['ID', 'stores', 'X', 'Y', 'road_address', 'place_url'])

print('total_result_number = ' , len(df))

print(df)
df.to_csv("crawled.csv", mode='w')

#make_map(df)