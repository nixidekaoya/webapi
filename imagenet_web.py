#!/usr/bin/env python

import flask
import random
import requests
import json
import os
import io
from PIL import Image
from flask import render_template

#Global file path and urls#

#file path
file_path = os.path.dirname(__file__)

temp_image_file = os.path.join(file_path,"static/temp_image.jpg")
imagenet_synset_file = os.path.join(file_path,"imagenet_synset.txt")

#URLs imagenet API
imagenet_synset_list_url = "http://www.image-net.org/api/text/imagenet.synset.obtain_synset_list"
imagenet_words_obtain_url = "http://www.image-net.org/api/text/wordnet.synset.getwords"
imagenet_geturl_url = "http://www.image-net.org/api/text/imagenet.synset.geturls"


#Dictaionary and lists
wnid_payload = {"wnid":""}
wnid_set = []
with open(imagenet_synset_file) as f:
    for line in f.readlines():
        line = line.replace("\n","")
        wnid_set.append(line)
wnid_num = len(wnid_set)
print(wnid_num)

#web_api
api_name = "Imagenet_web"
ip_addr = "192.168.0.116"
ip_port = 8002
app = flask.Flask(api_name)

#Global functions

def fetch_wnid_name(wnid):
    wnid_payload["wnid"] = wnid
    results = requests.get(imagenet_words_obtain_url,params = wnid_payload)
    name_list = results.text.split("\n")
    name_list.remove("")
    return name_list

def fetch_image_url(wnid = "rand"):
    if wnid == "rand":
        wnid_index = random.randint(0,wnid_num)
        wnid = wnid_set[wnid_index]
        wnid_payload["wnid"] = wnid
        results = requests.get(imagenet_geturl_url,params = wnid_payload)
        if results.status_code == 200:
            url_list = results.text.split("\n")
            while "" in url_list:
                url_list.remove("")
            return url_list,wnid
    else:
        wnid_payload["wnid"] = wnid
        results = requests.get(imagenet_geturl_url,params = wnid_payload)
        if results.status_code == 200:
            url_list = results.text.split("\n")
            url_list.remove("")
            while "" in url_list:
                url_list.remove("")
            return url_list,wnid
    

#Web api functions#
        
@app.route('/helloworld/',methods = ['GET'])
def helloworld():
    return "hello world!"

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route('/home/',methods = ['GET'])
def home():
    url_list,wnid = fetch_image_url(wnid = "rand")
    print(url_list)
    while url_list == None:
        url_list,wnid = fetch_image_url(wnid = "rand")
    image_num = len(url_list)
    print(image_num)
    url_index = random.randint(0,image_num)
    print(url_index)
    print(url_list[url_index])
    results = requests.get(url_list[url_index])
    print(results.status_code)
    fetch_counter= 0
    while results.status_code != 200:
        print(fetch_counter)
        fetch_counter += 1
        url_index = random.randint(0,image_num)
        print(url_list[url_index])
        results = requests.get(url_list[url_index])
        print(results.status_code)
        if fetch_counter > image_num:
            url_list,wnid = fetch_image_url(wnid = "rand")
            while url_list == None:
                url_list,wnid = fetch_image_url(wnid = "rand")
            image_num = len(url_list)
            url_index = random.randint(0,image_num)
            results = requests.get(url_list[url_index])
            fetch_counter = 0

    image_name_list = fetch_wnid_name(wnid)
    print(image_name_list)
    image_file_object = Image.open(io.BytesIO(results.content))
    image_file_object.save(temp_image_file)
    return render_template('imagenet_web.html')


#Run here#
if __name__ == "__main__":
    #fetch_image_url(wnid = "n02084071")
    #print(fetch_wnid_name(wnid = "n02084071"))
    app.run(debug = False, host = ip_addr, port = ip_port)
