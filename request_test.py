#!/usr/bin/env python

import requests
import json
import io
from PIL import Image

url = "http://192.168.0.116:8001/yolov3/detect/"
hw_url = "http://192.168.0.116:8001/helloworld/"
image_file_path = "/home/mofei/51.jpeg"

files = {'image':open(image_file_path,'rb')}
data_json = {}
data_json["sequence"] = 0

r =requests.get(hw_url)
print(r.text)

r = requests.post(url,data = data_json,files = files)
print(r.text)
