#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import json
import databasehandler
import time
import io
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from nltk.corpus import wordnet as wn
from pandas import DataFrame
import pandas as pd
import numpy as np

ip = "localhost"

wnid_list_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
chinese_translate_file_path  ="/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file_path = "/home/li/datasets/imageinfo_wnid_japanese.txt"
username = "li"
passwd = "issysesosakau"
database_name = "ImagenetDBT"
image_table = "ImageInfo"
map_table = "SynsetMap"
userinfo_table = "UserInfo"
level_table = "LevelTable"
preference_table = "ImagePreference"
relativity_table = "ImageRelativity"

db = databasehandler.DatabaseMySQL(ip,username,passwd,database_name)
example_dic = {"UserName":"LI Mofei","UserID":0,"ImageID":0,"Preference":"like","Known":"yes"}
user_info_columns = ["UserName","UserID"]
level_column = ["PreferenceNum"]

columns = ["SynsetWNID","SynsetName"]
columns_imagetable = ["Class0WNID"]

where_dic = {}
where_dic["UserName"] = "li mofei"
preference_columns = ["Preference","ImageClassWNID"]


save_image_path_png = "/home/li/datasets/wordcloud.png"
save_image_path_jpg = "/home/li/datasets/wordcloud.jpg"


base_path = "/home/li/webapi/"
user_path = base_path + "user/"
japanese_fonts_path = "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
broken_image_list_path = "/home/li/datasets/broken_list_id.txt"


japanese_wn_path = "/home/li/datasets/temp_japanese_wn.txt"
valid_wnid_list_path = "/home/li/datasets/valid_wnid_list.txt"
valid_wnid_list_name_path = "/home/li/datasets/valid_wnid_list_name.txt"

english_dic = {}
chinese_dic = {}
japanese_dic = {}
wnid_list = []
level_list = []

################## Translate
english_dic = {}
chinese_dic = {}
japanese_dic = {}
wnid_list = []



with open(valid_wnid_list_path,'r') as wnid_f:
    for line in wnid_f.readlines():
        wnid_list.append(str(line[:9]))

print(len(wnid_list))


########################  Generate word similarity Matrix
from nltk.corpus import wordnet_ic


similarity_list = ['Lin']
#print(brown_ic)
ic = wordnet_ic.ic('ic-semcor.dat')

def wn_similarity(synset_1,synset_2,similarity = 'Shortest_Path'):
    if similarity == "Shortest_Path":
        sim = wn.path_similarity(synset_1,synset_2)
    elif similarity == "Leacock_Chodorow":
        sim = wn.lch_similarity(synset_1,synset_2)
    elif similarity == "Wu_Palmer":
        sim = wn.wup_similarity(synset_1,synset_2)
    elif similarity == "Resnik":
        sim = synset_1.res_similarity(synset_2,ic)
    elif similarity == "Jiang_Conrath":
        sim = synset_1.jcn_similarity(synset_2,ic)
    elif similarity == "Lin":
        sim = synset_1.lin_similarity(synset_2,ic)
    else:
        sim = 0
    return sim


for similarity in similarity_list:
    np_matrix = np.zeros((len(wnid_list),len(wnid_list)),float)
    print(similarity)
    matrix_path = "/home/li/datasets/csv/" + str(similarity) + "_similarity_" + str(len(wnid_list)) + ".csv"
    for i in range(len(wnid_list)):
        if i % 100 == 0:
            print(i)
        wnid_1 = wnid_list[i]
        offset_1 = str(wnid_1[1:]) + "n"
        synset_1 = wn.of2ss(offset_1)
        for j in range(len(wnid_list) - i):
            wnid_2 = wnid_list[j + i]
            offset_2 = str(wnid_2[1:]) + "n"
            synset_2 = wn.of2ss(offset_2)
            np_matrix[i][j] = wn_similarity(synset_1,synset_2,similarity = similarity)
            np_matrix[j][i] = np_matrix[i][j]
    df1 = DataFrame(np_matrix,index = wnid_list, columns = wnid_list)
    df1.to_csv(matrix_path)


################### Choose Valid Synsets from Japanese wordnet
'''

japanese_wn_list = []

with open(japanese_wn_path,'r') as jp_wn_f:
    for line in jp_wn_f.readlines():
        
        japanese_wn_list.append(str(line[:9]))

print(japanese_wn_list[0])


valid_wnid_file = open(valid_wnid_list_path,'w')
count = 0

re = db.selectdistinct(image_table,columns_imagetable)
for wnid_taple in re:
    wnid = str(wnid_taple[0])
    if wnid in japanese_wn_list:
        valid_wnid_file.write(wnid + "\n")
        count += 1

print(count)

valid_wnid_file.close()
'''

######################################  Get Synsets name and Translation



'''
with io.open(japanese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        
        japanese = l_list[2]
        
        japanese_dic[wnid] = japanese



with io.open(chinese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        english = l_list[1]
        chinese = l_list[2]
        chinese_dic[wnid] = chinese
        english_dic[wnid] = english



#print(wnid_list)
category_num = len(wnid_list)
print(category_num)

'''

####################  Get Name and translation

'''
name_file = open(valid_wnid_list_name_path,'w')

for wnid in wnid_list:
    english = english_dic[str(wnid)]
    chinese = chinese_dic[str(wnid)]
    japanese = japanese_dic[str(wnid)]
    name_file.write(str(wnid) + "," + str(english) + "," + japanese.encode('utf-8') + "," + chinese.encode('utf-8') + "\n")

name_file.close()

'''


###################### Delete Invalid Images
'''
relativity_dic = {}
thisuser = "fan"
current_user_path = user_path + str(thisuser) + "/"
where_dic = {}
where_dic["IndexID"] = str(57)
columns_imagetable_2 = ["IndexID","ImageName","Path"]

db.delete(image_table,condition_dic = where_dic)



for i in range(index_max):
    
    where_dic = {}
    where_dic["IndexID"] = str(i)
    re = db.select(image_table,columns_imagetable_2,condition_dic = where_dic)
    if len(re) == 0:
        continue
    else:
        result = re[0]
        indexid = int(result[0])
        file_path = str(result[2]) + str(result[1]) + ".jpg"
        info = os.popen("file -b " + file_path).read()
        if info.startswith("HTML"):
            where_dic = {}
            where_dic["IndexID"] = str(indexid)
            db.delete(image_table,condition_dic = where_dic)
            print(str(indexid))
            with open(broken_image_list_path,'a') as broken_f:
                broken_f.write(str(indexid) + "\n")
            
    
'''


#################### Count Preference and Relativity data numbers
'''
preference_number_count_path = "/home/li/datasets/statistics/preference_count.txt"
relativity_number_count_path = "/home/li/datasets/statistics/relativity_count.txt"

preference_number_count_valid = "/home/li/datasets/statistics/preference_count_valid.txt"
relativity_number_count_valid = "/home/li/datasets/statistics/relativity_count_valid.txt"


columns = ["UserName","UserID"]

preference_number_dic = {}
preference_valid_number_dic  = {}

preference_total = 0
preference_valid_total = 0

re = db.selectdistinct(preference_table,columns)
for user in re:
    counter = 0
    username = str(user[0])
    userid = int(user[1])
    preference_column = ["ImageClassWNID"]
    where_dic = {}
    where_dic["UserName"] = username
    result = db.select(preference_table,preference_column,condition_dic = where_dic)
    total_number = len(result)
    preference_total += total_number
    preference_number_dic[username] = int(total_number)
    for result_class in result:
        wnid = str(result_class[0])
        if wnid in wnid_list:
            counter += 1

    preference_valid_number_dic[username] = int(counter)
    preference_valid_total += counter

with open(preference_number_count_path,'w') as p_f:
    for user in preference_number_dic.keys():
        p_f.write(str(user) + "\t" + str(preference_number_dic[user]) + "\n")
    p_f.write("total:" + "\t" + str(preference_total) + "\n")
        
with open(preference_number_count_valid,'w') as p_f:
    for user in preference_valid_number_dic.keys():
        p_f.write(str(user) + "\t" + str(preference_valid_number_dic[user]) + "\n")
    p_f.write("total:" + "\t" + str(preference_valid_total) + "\n")


relativity_number_dic = {}
relativity_valid_number_dic = {}

relativity_total = 0
relativity_valid_total = 0

re = db.selectdistinct(relativity_table,columns)
for user in re:
    counter = 0
    username = str(user[0])
    userid = int(user[1])
    relativity_column = ["ImageClassWNID_1","ImageClassWNID_2"]
    where_dic = {}
    where_dic["UserName"] = username
    result = db.select(relativity_table,relativity_column,condition_dic = where_dic)
    total_number = len(result)
    relativity_number_dic[username] = int(total_number)
    relativity_total += int(total_number)
    for result_class in result:
        wnid_1 = str(result_class[0])
        wnid_2 = str(result_class[1])
        if wnid_1 in wnid_list:
            if wnid_2 in wnid_list:
                counter += 1

    relativity_valid_number_dic[username] = int(counter)
    relativity_valid_total += int(counter)

with open(relativity_number_count_path,'w') as p_f:
    for user in relativity_number_dic.keys():
        p_f.write(str(user) + "\t" + str(relativity_number_dic[user]) + "\n")
    p_f.write("total:" + "\t" + str(relativity_total) + "\n")
        
with open(relativity_number_count_valid,'w') as p_f:
    for user in relativity_valid_number_dic.keys():
        p_f.write(str(user) + "\t" + str(relativity_valid_number_dic[user]) + "\n")
    p_f.write("total:" + "\t" + str(relativity_valid_total) + "\n")


'''


############  Relativity Matrix Generation


'''

user_list = ["li mofei","nishi","ise","nakamura","yue zixiang","ustyui","jiao","fan","yg","luis","ebube","archer"]
id_list = []
id_index_dic = {}
unknown_id_list = []
relativity_dic = {}

index_max = 85338
index_ = 1

columns = ["ImageClassWNID_1","ImageClassWNID_2","Relativity"]
where_dic = {}
user = "nakamura"


relativity_csv_path = "/home/li/webapi/user/" + str(user) + "/" + str(user) + "_relativity.csv"

figure_file = "/home/li/datasets/images/" + str(user) + "_relativity.jpg"

t1  = time.time()

#print(re)

for user in user_list:
    where_dic["UserName"] = user
    re = db.select(relativity_table,columns,condition_dic = where_dic)
    relativity_matrix_file = "/home/li/datasets/images/" + str(user) + "_relativity.csv"
    id_list = []
    for result in re:
        wnid_1 = result[0]
        wnid_2 = result[1]

        if wnid_1 not in wnid_list:
            continue

        if wnid_2 not in wnid_list:
            continue
    
        if wnid_1 not in id_list:
            relativity_dic[wnid_1] = {wnid_1:int(1)}
            id_list.append(wnid_1)
        relativity = result[2]
    
        if relativity == "NULL":
            unknown_id_list.append(wnid_2)
        else:
            if wnid_2 not in id_list:
                id_list.append(wnid_2)
                relativity_dic[wnid_2] = {wnid_2:int(1)}
            if relativity == "yes":
                relativity_dic[wnid_1][wnid_2] = int(1)
                relativity_dic[wnid_2][wnid_1] = int(1)
            elif relativity == "no":
                relativity_dic[wnid_1][wnid_2] = int(-1)
                relativity_dic[wnid_2][wnid_1] = int(-1)
        


    for i in range(len(id_list)):
        id_index_dic[id_list[i]] = i

    np_matrix = np.zeros((len(id_list),len(id_list)),int)
    for wnid in id_list:
        re_dic = relativity_dic[wnid]
        for sub_wnid in re_dic.keys():
            np_matrix[id_index_dic[wnid]][id_index_dic[sub_wnid]] = int(re_dic[sub_wnid])
    

    df1 = DataFrame(np_matrix,index = id_list, columns = id_list)
    df1.to_csv(relativity_matrix_file)



'''

########### Draw relativity matrix
'''
print(time.time() - t1)
print(df1)
print(len(id_list))

cdict = ['#FF0000','#FFFFFF','#0000FF']
my_cmap = colors.ListedColormap(cdict,'indexed')

plt.imshow(np_matrix,cmap = my_cmap,interpolation = "nearest")
#plt.xticks(range(len(id_list)),id_list,rotation = 90)
#plt.yticks(range(len(id_list)),id_list)
plt.colorbar()
plt.savefig(figure_file)
plt.show()
'''





################ User Preference Matrix generation

'''
user_list = ["li mofei","nishi","nakamura","yue zixiang","ustyui","jiao","fan","yg","luis","ebube","archer","ise","yoshikawa"]
preference_columns = ["ImageClassWNID","Preference"]
matrix_dic = {}
where_dic = {}

preference_matrix_path = "/home/li/datasets/images/preference_matrix_interface_v2.csv"


id_list = []
print(np.empty((5,2),int))


for user in user_list:
    matrix_dic[user] = {}
    where_dic["UserName"] = str(user)
    re = db.select(preference_table,preference_columns,condition_dic = where_dic)
    for result in re:
        wnid = str(result[0])
        if wnid not in wnid_list:
            continue

        if wnid not in id_list:
            id_list.append(wnid)

        preference = str(result[1])
        if preference == "like":
            matrix_dic[user][wnid] = int(1)
        elif preference == "dislike":
            matrix_dic[user][wnid] = int(-1)
        elif preference == "neutral":
            matrix_dic[user][wnid] = int(0)
        

print(len(id_list))
matrix = np.zeros((len(user_list),len(id_list)),int)* np.nan
for i in range(len(user_list)):
    user = user_list[i]
    for j in range(len(id_list)):
        wnid = id_list[j]
        if wnid in matrix_dic[user].keys():
            matrix[i,j] = matrix_dic[user][wnid]




df1 = DataFrame(matrix,index = user_list,columns = id_list)
df1.to_csv(preference_matrix_path)
print(df1.shape)
#print(df1)
'''

################### Draw Preference Matrix Plot
'''
cdict = ['#FF0000','#000000','#0000FF']
my_cmap = colors.ListedColormap(cdict,'indexed')

plt.matshow(matrix,cmap = my_cmap,interpolation = "nearest")
#plt.xticks(range(len(id_list)),id_list,rotation = 90)
plt.yticks(range(len(user_list)),user_list)
plt.colorbar()
plt.show()
'''



db.close()
