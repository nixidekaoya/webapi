#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import json
import databasehandler
import time
import io
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

ip = "localhost"

wnid_list_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
chinese_translate_file_path  ="/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file_path = "/home/li/datasets/imageinfo_wnid_japanese.txt"
broken_list_path = "/home/li/datasets/broken_list_id.txt"
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

japanese_fonts_path = "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"


english_dic = {}
chinese_dic = {}
japanese_dic = {}
wnid_list = []
level_list = []

image_columns = ["IndexID","ImageName","Path"]

re = db.select(image_table,image_columns)
broken_file = open(broken_list_path,'a')

print(re)

'''
for result in re:
    indexid = str(result[0])
    file_path = str(result[2]) + str(result[1]) + ".jpg"
    info = os.popen("file -b " + file_path).read()
    if info.startswith("HTML"):
        broken_file.write(indexid + "\n")

'''

broken_file.close()

'''
re = db.selectdistinct(image_table,columns_imagetable)
for wnid_taple in re:
    wnid_list.append(wnid_taple[0])



with io.open(japanese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        english = l_list[1]
        japanese = l_list[2]
        english_dic[wnid] = english
        japanese_dic[wnid] = japanese



with io.open(chinese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        chinese = l_list[2]
        chinese_dic[wnid] = chinese


result_1 = db.select(level_table,level_column)
for level in result_1:
    level_list.append(int(level[0]))
    

result = db.select(preference_table,preference_columns,where_dic)
record_num = len(result)

#print(result)
like_list = []
like_dic = {}
dislike_list = []
dislike_dic = {}
neutral_list = []
neutral_dic = {}
for record in result:
    preference = str(record[0])
    wnid = str(record[1])
    if preference == "like":
        if wnid in like_list:
            like_dic[wnid] += 1
        else:
            like_dic[wnid] = 1
        like_list.append(wnid)
    elif preference == "dislike":
        if wnid in dislike_list:
            dislike_dic[wnid] += 1
        else:
            dislike_dic[wnid] = 1
        dislike_list.append(wnid)
    else:
        if wnid in neutral_list:
            neutral_dic[wnid] += 1
        else:
            neutral_dic[wnid] = 1
        neutral_list.append(wnid)


frequencies = {}
for wnid in like_list:
    frequencies[chinese_dic[wnid]] = int(like_dic[wnid])


#print(frequencies)
wordcloud = WordCloud(font_path = chinese_fonts_path,width = 500, height = 200, prefer_horizontal = 0.9, max_words = 50, max_font_size = 20, background_color = 'white').fit_words(frequencies)
plt.imshow(wordcloud)

plt.axis("off")
plt.savefig(save_image_path_jpg)
print(type(wordcloud))


'''

'''

re = db.selectdistinct(userinfo_table,user_info_columns)
user_id_list = {}




for user in re:
    
    user_id_list[user[0]] = int(user[1])
    user_name = str(user[0])
    user_id = int(user[1])
    userinfo_dic = {}
    where_dic = {}
    where_dic["UserName"] = user_name

    result_2 = db.count(preference_table,condition_dic = where_dic)
    userinfo_dic["PreferenceNumber"] = str(result_2)
    result_2 = db.count(relativity_table,condition_dic = where_dic)
    userinfo_dic["RelativityNumber"] = str(result_2)
    userinfo_dic["SimilarityNumber"] = str(0)

    userinfo_dic["PreferenceLevel"] = str(0)
    userinfo_dic["RelativityLevel"] = str(0)
    userinfo_dic["SimilarityLevel"] = str(0)

        
    for i in range(1,len(level_list)+1):
        if int(userinfo_dic["PreferenceNumber"]) >= level_list[i-1]:
            userinfo_dic["PreferenceLevel"] = str(i)
        if int(userinfo_dic["RelativityNumber"]) >= level_list[i-1]:
            userinfo_dic["RelativityLevel"] = str(i)
        if int(userinfo_dic["SimilarityNumber"]) >= level_list[i-1]:
            userinfo_dic["SimilarityLevel"] = str(i)
        
    db.update(userinfo_table,userinfo_dic,where_dic)
    
    
    print(result_2)

print(user_id_list)


wnid_list = []

#result = db.selectdistinct(map_table,columns)
#print(len(result))
count = 0
t1 = time.time()
'''




'''

counter = 0
base = 5

for i in range(101):
    level_dic = {}
    level_dic["level"] = int(i)
    #print(counter)
    counter = counter +  base + i
    level_dic["PreferenceNum"] = counter
    level_dic["RelativityNum"] = counter
    level_dic["SimilarityNum"] = counter
    db.insert(level_table,level_dic)
    
    

print(counter)

''' 

'''
re = db.selectdistinct(image_table,columns_imagetable)
for wnid_taple in re:
    wnid_list.append(wnid_taple[0])

print(len(wnid_list))
'''


'''
trans_file = open(wnid_list_path,'w')

for synset in result:
    dic = {}
    wnid = synset[0]
    synsetname = synset[1]
    count += 1
    print(str(count) + ":")
    strlist = str(synsetname).split(',')
    print(synsetname)
    try:
        trans_chinese = translate_client.translate(str(synsetname),target_language = "zh-CN")
        trans_japanese = translate_client.translate(str(synsetname),target_language = "ja")
        chin = trans_chinese["translatedText"]
        jap = trans_japanese["translatedText"]
    except Exception as e:
        print(type(e))
        print(e.args)
        chin = "NULL"
        jap = "NULL"


    print(chin)
    print(jap)
    update_dic = {}
    update_dic["SynsetName_japanese"] = str("NULL")
    update_dic["SynsetName_chinese"] = str("NULL")
    condition_dic = {}
    condition_dic["SynsetWNID"] = str(wnid)

    trans_file.write(str(wnid) + "\t" + str(synsetname) + "\t" + chin.encode('utf-8') + "\t" + jap.encode('utf-8') + "\n")
    #db.update(map_table,update_dic,condition_dic)

    #result = db.select(map_table,columns_la,condition_dic)
    #result = result[0]
    #for re in result:
        #print(re)
    
    #dic["SynsetWNID"] = str(wnid)
    #dic["SynsetName"] = str(synsetname)
    #db.insert(map_table,dic)
    
t2 = time.time()-t1
print("Time consume:" + str(t2))

trans_file.close()
'''

db.close()
