#!/usr/bin/env python

import requests
import json
import os
import io
from PIL import Image

file_path = os.path.dirname(__file__)
temp_image_file = os.path.join(file_path,"static/temp_image.jpg")
imagenet_synset_file = os.path.join(file_path,"imagenet_synset.txt")
imagenet_synset_list_url = "http://www.image-net.org/api/text/imagenet.synset.obtain_synset_list"
imagenet_words_obtain_url = "http://www.image-net.org/api/text/wordnet.synset.getwords"
imagenet_geturl_url = "http://www.image-net.org/api/text/imagenet.synset.geturls"

test_fail_url = "http://www.zoo.gov.tw/epaper/images/20051021_02.jpg"
test_image_url = "http://farm2.static.flickr.com/1305/925581277_5f6518bb4f.jpg"
testwnid = "n02503127"

wnid_payload = {"wnid":testwnid}

#result = requests.get(imagenet_synset_list_url)
#with open(imagenet_synset_file,"w") as f:
#    f.write(result.text)

#result = requests.get(imagenet_geturl_url,params = wnid_payload)
image_result = requests.get(test_image_url)
print(image_result.status_code)
image_result = requests.get(test_fail_url)
print(image_result.status_code)
#i = Image.open(io.BytesIO(image_result.content))
#i.save(temp_image_file)
#print(result.text)
