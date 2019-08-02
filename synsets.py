#!/usr/bin/env python
#coding:utf-8

import json
import sys
import codecs
import io
import os
import databasehandler
from nltk.corpus import wordnet as wn
import nltk
import matplotlib.pyplot as plt



synsets_path = "/home/li/datasets/Imagenet_synsets/" 
base_synset = wn.synsets("entity")[0]
second_synsets = base_synset.hyponyms()

synset_count = []
synset_count.append(1)
hierarchy_num = 20
synset_list = []
synset_list_name = []
synset_list.append(base_synset)

#print(wn.langs())

for synset in second_synsets:
    ln = synset.lemma_names(lang='cmn')
    for lemmaname in ln:
        print(lemmaname)
       

for i in range(hierarchy_num):
    print("Layer " + str(i) + ":\n")
    synsets_fn_jp = "jp/Imagenet_Synsets_" + str(i) + "_jp_layer.txt"
    synsets_fn_en = "en/Imagenet_Synsets_" + str(i) + "_en_layer.txt"
    synsets_fn_ch = "ch/Imagenet_Synsets_" + str(i) + "_ch_layer.txt"
    file_path_jp = synsets_path + synsets_fn_jp
    file_path_en = synsets_path + synsets_fn_en
    file_path_ch = synsets_path + synsets_fn_ch
    file_write_jp = codecs.open(file_path_jp,'w',encoding="utf-8")
    file_write_en = codecs.open(file_path_en,'w',encoding="utf-8")
    file_write_ch = codecs.open(file_path_ch,'w',encoding="utf-8")
    
    synset_num = 0
    for synset in synset_list:
        synset_num += len(synset.hyponyms())
    synset_count.append(synset_num)
    old_synset_list = synset_list
    
    synset_list = []
    for synset in old_synset_list:
        p_str=u""
        
        ln_jp = synset.lemma_names(lang='jpn')
        for lemmaname in ln_jp:
            file_write_jp.write(lemmaname)
            file_write_jp.write(u",")
        file_write_jp.write(u"\n")
        ln_en = synset.lemma_names()
        for lemmaname in ln_en:
            file_write_en.write(lemmaname)
            file_write_en.write(u",")
        file_write_en.write(u"\n")
        ln_ch = synset.lemma_names(lang='cmn')

        
        for lemmaname in ln_ch:
            file_write_ch.write(lemmaname)
            file_write_ch.write(u",")
            p_str += lemmaname + ","

        #print(p_str)
        file_write_ch.write(u"\n")

        
        hypon_synset = synset.hyponyms()
        for h_synset in hypon_synset:
            synset_list.append(h_synset)

    file_write_en.close()
    file_write_jp.close()
    file_write_ch.close()


print(synset_count)
print(sum(synset_count))
print(len(synset_list_name))
for name in synset_list_name:
    print(name)
plt.bar(range(len(synset_count)),synset_count)
for i in range(len(synset_count)):
    plt.text(i - 1,synset_count[i] + 300,str(synset_count[i]),horizontalalignment = "left",fontsize = 12)
#plt.show()
