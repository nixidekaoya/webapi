#!/usr/bin/env python2
# -*- coding: UTF-8 -*-


import httplib
import md5
import urllib
import io
import random
import time
import requests
import json

translate_file_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
baidu_translate_file_path = "/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file = "/home/li/datasets/imageinfo_wnid_japanese.txt"



japanese_wordnet_file_path = "/home/li/datasets/wnjpn-ok.tab"
temp_japanese_wn_file = "/home/li/datasets/temp_japanese_wn.txt"
counter = 0



japanese_wn_dic = {}
japanese_google_dic = {}
japanese_wn_list = []

japanese_f = open(japanese_translate_file,"w")

with io.open(temp_japanese_wn_file,'r',encoding = "utf-8") as jpwn_f:
    for line in jpwn_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        japanese = l_list[1]
        japanese_wn_list.append(wnid)
        japanese_wn_dic[wnid] = japanese


with io.open(translate_file_path,'r',encoding = "utf-8") as jpwn_f:
    for line in jpwn_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        english = l_list[1]
        if wnid in japanese_wn_list:
            japanese = japanese_wn_dic[wnid]
        else:
            japanese = l_list[3]

        japanese_f.write(str(wnid) + "\t" + str(english) + "\t" + japanese.encode("utf-8") + "\n")
       


japanese_f.close()




'''
with io.open(baidu_translate_file_path,'r',encoding = "utf-8") as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        print(l_list[2])
'''


'''
baidu_trans_file = open(baidu_translate_file_path,'a')


httpClient = None
httpClient = httplib.HTTPSConnection('api.fanyi.baidu.com')

appid = '20190219000268837'
secretkey = '2G4bthTQiLMAwkfLwfDv'



myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
fromLang = 'en'
toLang = 'zh'

start_index = 10793

counter = start_index
t1 = time.time()

with io.open(translate_file_path,'r',encoding = 'utf-8') as translate_f:
    for line in translate_f.readlines()[start_index:]:
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        english = l_list[1]

        counter += 1
        print(counter)
        print(english)

        english_list = english.split(',')
        if len(english_list) > 3:
            english = english_list[0] + ',' + english_list[1] + ',' + english_list[2]

        salt = random.randint(32768,65535)

        sign = appid+english+str(salt)+secretkey
        ml = md5.new()
        ml.update(sign)
        sign = ml.hexdigest()
        longurl = myurl + '?appid=' + appid + '&q=' + urllib.quote(english) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign


        payload = {}
        payload["q"] = english
        payload["from"] = fromLang
        payload["to"] = toLang
        payload["appid"] = appid
        payload["salt"] = str(salt)
        payload["sign"] = sign
        
        response = requests.get(myurl,params = payload)
        result = response.text
        
        print(result)
        print(response.status_code)
        trans_result = json.loads(result)

        result = trans_result["trans_result"]
        result = result[0]
        trans_result = result["dst"]

       
        
        print(trans_result)
        baidu_trans_file.write(str(wnid) + "\t" + str(english) + "\t" + trans_result.encode('utf-8') + "\n")

            
if httpClient:
    httpClient.close()

baidu_trans_file.close()
t2 = time.time() - t1
print(t2)
'''
