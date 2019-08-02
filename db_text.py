#!/usr/bin/env python2
# -*- coding: UTF-8 -*-



import json
import databasehandler
import time
import random
import chardet
import io
import os
from wordcloud import WordCloud
from nltk.corpus import wordnet as wn
import matplotlib.pyplot as plt
import Image, ImageFont, ImageDraw
import pandas as pd


ip = "localhost"


wnid_list_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
valid_wnid_list_path = "/home/li/datasets/valid_wnid_list.txt"
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
raw_record_table = "ItemDataRawRecord"
raw_data_table = "ItemDataRaw"
domain_table = "DomainItem"
lifelog_table = "LifeLogItem"
lifelog_data_table = "LifeLogItemDataRaw"



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

english_fonts_path = "/home/li/webapi/font/ubuntu-font-family/Ubuntu-B.ttf"
japanese_fonts_path = "/home/li/webapi/font/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/home/li/webapi/font/wqy/wqy-microhei.ttc"


english_word_path = "/home/li/datasets/english_word.txt"
japanese_word_path = "/home/li/datasets/japanese_word.txt"
chinese_word_path = "/home/li/datasets/chinese_word.txt"
information_path = "/home/li/datasets/information.txt"


domain_list_path = "/home/li/datasets/domain/domain_list.txt"
domain_table_path = "/home/li/datasets/domain/item_table.txt"
domain_item_name_path = "/home/li/datasets/domain/item_name.txt"
domain_item_image_folder = "/home/li/datasets/domain/domain_image/"


english_dic = {}
chinese_dic = {}
japanese_dic = {}
wnid_list = []
level_list = []

columns = ["RecordID"]
where_dic = {}
where_dic["UserName"] = str("test2")
re = db.selectmax(raw_data_table,columns,where_dic)
print(re==None)


################ Data Fetch

data_f = pd.DataFrame()

where_dic = {}
user_name = "nakamura"
where_dic["UserName"] = str(user_name)


columns = ["UserRecordID","UserID","UserName","ItemID","ItemName","CoordinatesX","CoordinatesY"]
re = db.select(lifelog_data_table,columns,where_dic)

record_list = []
user_id_list = []
user_name_list = []
item_id_list = []
item_name_list = []
coordinatesX_list = []
coordinatesY_list = []

for record in re:
    record_list.append(int(record[0]))
    user_id_list.append(int(record[1]))
    user_name_list.append(str(record[2]))
    item_id_list.append(str(record[3]))
    item_name_list.append(str(record[4]))
    coordinatesX_list.append(float(record[5]))
    coordinatesY_list.append(float(record[6]))

data_f = pd.DataFrame({"RecordID":record_list,
                      "UserID":user_id_list,
                      "UserName":user_name_list,
                      "ItemID":item_id_list,
                      "ItemName":item_name_list,
                      "X-Coordinate":coordinatesX_list,
                      "Y-Coordinate":coordinatesY_list})
print(data_f)
data_f.to_csv("/home/li/torch/data/Group1_nakamura_no_164_20190605.csv")

############################## Life Log item Insert
'''

lifelog_itemlist = "/home/li/datasets/lifelog/itemlist.csv"
data = pd.read_csv(lifelog_itemlist)
image_path = "/home/li/datasets/lifelog/lifelog_domain/"

#translate_f = open(translate_path,'w')
#print(data.index)
#print(data.columns)
print(data.loc[1,"Name"])


sample_list = []
item_number = 256
item_eva = 8
circle = int(item_number/item_eva)
sample = random.sample(range(1,item_number+1),item_number)
for i in range(circle):
    eva_sample = sample[item_eva * i: item_eva * (i + 1)]
    sample_list.append(eva_sample)
    
print(len(sample_list))

condition_dic = {}
condition_dic["ItemID"] = str(23)
columns = ["ImagePath"]


for i in range(1,item_number + 1):
    where_dic = {}
    where_dic["ItemID"] = str(i)
    columns = ["ImageName"]
    print(i)
    re = db.select(lifelog_table,columns,where_dic)
    print(re)
    imagename = re[0][0]
    path = image_path + imagename
    update_dic = {}
    update_dic["ImagePath"] = str(path)
    if os.path.isfile(path):
        db.update(lifelog_table,update_dic,where_dic)
    else:
        print("Not exists:" + str(path))



print(data.columns)

for index,row in data.iterrows():
    insert_dic = {}
    insert_dic["ItemID"] = str(row["ID"])
    insert_dic["ItemName"] = str(row["Name"])
    insert_dic["ImageName"] = str(row["filename"])
    insert_dic["ImagePath"] = str(image_path) + str(row["filename"])
    insert_dic["Description"] = str(row["description"])
    ch_name = row["Chinese name"]
    jp_name = row["Japanese name"]

    if os.path.isfile(str(insert_dic["ImagePath"])):
        i = 1
    else:
        print(str(insert_dic["ImagePath"]))
    
    print(ch_name)
    print(type(ch_name))
    print(chardet.detect(ch_name))
    print(jp_name)
    descrip_text = str(row["Name"]) + "\t" + ch_name + "\t" + jp_name + "\t" + str(row["description"]) + "\n"
    print(descrip_text)
    
    db.insert(lifelog_table,insert_dic)

'''
#translate_f.close()


############################# Domain item insert

'''
domain_list = []

columns = ["ItemID","ItemDomainID","ItemName","ItemImagePath"]

where_dic = {}
where_dic["ItemDomain"] = "singer"

re = db.select(domain_table,columns,where_dic)
print(len(re))

#print(random.sample(range(len(re)),10))


with open(domain_list_path) as domain_list_file:
    for line in domain_list_file.readlines():
        domain_list.append(line.strip())


name_file = open(domain_item_name_path,'w')



with io.open(domain_table_path,'r',encoding = "utf-8") as domain_table_file:
    for line in domain_table_file.readlines():
        insert_dic = {}
        lines = line.strip().split(',')
        item_origin_name = lines[0]
        item_domain = lines[1]
        item_domain_id = lines[2]
        item_name = lines[3]
        item_image_path = domain_item_image_folder + str(item_domain) + "/" +  str(item_domain) + str(item_domain_id) + ".jpg"
        insert_dic["ItemDomain"] = str(item_domain)
        insert_dic["ItemDomainID"] = str(item_domain_id)
        insert_dic["ItemName"] = str(item_name)
        insert_dic["ItemImagePath"] = str(item_image_path)
        print(item_origin_name)
        name_file.write(str(item_name) + "\t" + item_origin_name.encode('utf-8') + "\n")
        db.insert(domain_table,insert_dic)
        #print(lines)

name_file.close()
'''


########################### text to picture
'''

temp_image_file = "/home/li/webapi/text2image.png"
text = u"水上潜水器";
im = Image.new("RGB",(200,40),(255,160,0))
dr = ImageDraw.Draw(im)
font = ImageFont.truetype(chinese_fonts_path,20)
dr.text((20,10),text,font = font, fill = "#000000")
im.show()
im.save(temp_image_file)
'''


############################information

'''
re = db.selectdistinct(image_table,columns_imagetable)
with open(valid_wnid_list_path,'r') as wnid_f:
    for line in wnid_f.readlines():
        wnid_list.append(str(line[:9]))




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


counter = 0
with open(information_path,'w') as word_f:
    for wnid in wnid_list:
        offset = str(wnid[1:]) + "n"
        english_words = english_dic[wnid]
        chinese_words = chinese_dic[wnid]
        japanese_words = japanese_dic[wnid]
        synset = wn.of2ss(offset)
        definition = str(synset.definition())
        examples = synset.examples()
        
        print(definition)
        if len(examples) >=1:
            example = examples[0]
            print(example)
            word_f.write(str(wnid) + ":" + english_words.encode('utf-8') + "\t" + japanese_words.encode('utf-8') + "\t" + chinese_words.encode('utf-8') + "\t" + str(definition) + "\t" + str(example) + "\n")
        else:
            word_f.write(str(wnid) + ":" + english_words.encode('utf-8') + "\t" + japanese_words.encode('utf-8') + "\t" + chinese_words.encode('utf-8') + "\t" + str(definition) + "\t" + "\n")

        
        
        #word_f.write(str(wnid) + "\t")
        #english_word = english_dic[wnid]
        #english_word_list = english_word.split(',')
        #english_word = english_word_list[0].strip()
        #print(jpwn)
        #counter += 1
        #if (counter > 30):
            #break
    


'''
#print(result)

'''
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
