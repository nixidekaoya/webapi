#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import sys
import os
import MySQLdb
import random


#Some useful functions define#

#FUNC convert pairs of list or tuple to dictionary#
'''
@param:
    keys: key list, type:list
    values: value list, type:list
@return:
    dic:dictionary
'''
def todictionary(keys,values):
    dic = {}
    #print(keys)
    #print(values)
    #print(len(keys))
    #print(len(values))
    for i in range(len(keys)):
        dic[keys[i]] = values[i]
    return dic


#DatabaseMySQL class#

class DatabaseMySQL(object):
    def __init__(self,ip,username,passwd,database_name):
        self.ip = ip
        self.username = username
        self.passwd = passwd
        self.database_name = database_name
        self.db = MySQLdb.connect(self.ip,self.username,self.passwd,self.database_name)
                

        
    #database_close#
    def close(self):
        self.db.close()

    #database_insert#
    def insert(self,table,record_dic):
        columns = str(tuple(record_dic.keys()))
        table = self.database_name + "." + table
        while "'" in columns:
            columns = columns.replace("'","")
        values = str(tuple(record_dic.values()))
        values = values.replace("\\","\\\\")
        sql = "INSERT INTO {0} {1} VALUES {2}".format(str(table),columns,values)
        print(sql)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        return


    #database update#
    def update(self,table,update_dic,condition_dic = ""):
        table = self.database_name + "." + table
        set_part = ""
        where_part = ""
        first = True
        for key in update_dic.keys():
            while "'" in key:
                key = key.replace("'","")
            if first == True:
                set_part = set_part + key + "='" + str(update_dic[key]) + "'"
                first = False
            else:
                set_part = set_part + "," + key + "='" + str(update_dic[key]) + "'"
            
        first = True
        if condition_dic != "":
            for key in condition_dic.keys():
                while "'" in key:
                    key = key.replace("'","")
                if first == True:
                    where_part = where_part + key + "='" + str(condition_dic[key]) + "'"
                    first = False
                else:
                    where_part = where_part + "," + key + "='" + str(condition_dic[key]) + "'"

        if where_part != "":
            sql = "UPDATE {0} SET {1} WHERE {2}".format(str(table),set_part,where_part)
        else:
            sql = "UPDATE {0} SET {1}".format(str(table),set_part)
        
        #print(sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        return

    #database delete#
    def delete(self,table,condition_dic):
        table = self.database_name + "." + table
        where_part = ""
        first = True
        for key in condition_dic.keys():
            while "'" in key:
                key = key.replace("'","")
            if first == True:
                where_part = where_part + key + "='" + str(condition_dic[key]) + "'"
                first = False
            else:
                where_part = where_part + "," + key + "='" + str(condition_dic[key]) + "'"
        sql = "DELETE FROM {0} WHERE {1}".format(str(table),where_part)
        #print(sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        return

    #database select#
    def select(self,table,columns = "*" , condition_dic = "",return_type = "all"):
        table = self.database_name + "." + table
        where_part = ""
        columns_part = ""
        first = True
        if columns != "*":
            for column in columns:
                if first == True:
                    columns_part += column
                    first = False
                else:
                    columns_part += "," + column
        else:
            columns_part = "*"

        first = True
        if condition_dic != "":
            for key in condition_dic.keys():
                while "'" in key:
                    key = key.replace("'","")
                if first == True:
                    where_part = where_part + key + "='" + str(condition_dic[key]) + "'"
                    first = False
                else:
                    where_part = where_part + "," + key + "='" + str(condition_dic[key]) + "'"

        if where_part != "":
            sql = "SELECT {0} FROM {1} WHERE {2}".format(columns_part,str(table),where_part)
        else:
            sql = "SELECT {0} FROM {1}".format(columns_part,str(table))
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        if return_type == "all":
            results = cursor.fetchall()
            return results
        elif return_type == "one":
            results = cursor.fetchone()
            return results

    #database count number#
    def count(self,table,condition_dic = ""):
        table = self.database_name + "." + table
        where_part = ""
        first = True
        if condition_dic != "":
            for key in condition_dic.keys():
                while "'" in key:
                    key = key.replace("'","")
                if first == True:
                    where_part = where_part + key + "='" + str(condition_dic[key]) + "'"
                    first = False
                else:
                    where_part = where_part + "," + key + "='" + str(condition_dic[key]) + "'"

        if where_part != "":
            sql = "SELECT COUNT(*) FROM {0} WHERE {1}".format(str(table),where_part)
        else:
            sql = "SELECT COUNT(*) FROM {0}".format(str(table))
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        results = cursor.fetchall()
        return int(results[0][0])

    #select random record#
    def selectrandom(self,table,columns = "*",condition_dic = ""):
        results = self.select(table,columns,condition_dic,return_type = "all")
        length = len(results)
        #print(length)
        random_index = random.randint(0,length - 1)
        sample = results[random_index]
        if columns == "*":
            keys = db.getcolumns(self,table,return_type = "list")
            dic = todictionary(keys,sample)
        else:
            dic = todictionary(columns,sample)
        return dic

    

    #get columns of table#
    def getcolumns(self,table,return_type = "list"):
        table = self.database_name + "." + table
        sql = "SHOW COLUMNS FROM {0}".format(str(table))
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        results = cursor.fetchall()
        if return_type == "list":
            column_list = []
            for column in results:
                column_list.append(column[0])
            return column_list
        elif return_type == "dictionary":
            column_dic = {}
            for column in results:
                column_dic[column[0]] = column[1]
            return column_dic
        else:
            print("Return Type Error!")
            return False


    #select distinct
    def selectdistinct(self,table,columns):
        table = self.database_name + "." + table
        first = True
        columns_part = "" 
        for column in columns:
            if first == True:
                columns_part += column
                first = False
            else:
                columns_part += "," + column
        
        sql = "SELECT DISTINCT {0} FROM {1}".format(columns_part,str(table))
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        re = cursor.fetchall()
        result = []
        for element in re:
            result.append(element[0])
        return re



    #count distinct
    def countdistinct(self,table,column):
        table = self.database_name + "." + table
        column_part = ""
        first = True
        for col in column:
            if first:
                column_part += str(col)
                first = False
            else:
                column_part += "," + str(col)
        sql = "SELECT COUNT(DISTINCT {0}) FROM {1}".format(str(column_part),str(table))
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        results = cursor.fetchall()
        return results[0][0]

    #select max of a column
    def selectmax(self,table,column,condition_dic = ""):
        table = self.database_name + "." + table
        column = column[0]
        where_part = ""
        first = True
        if condition_dic != "":
            for key in condition_dic.keys():
                while "'" in key:
                    key = key.replace("'","")
                if first == True:
                    where_part = where_part + key + "='" + str(condition_dic[key]) + "'"
                    first = False
                else:
                    where_part = where_part + "," + key + "='" + str(condition_dic[key]) + "'"

        if where_part == "":
            sql = "SELECT MAX({0}) FROM {1}".format(str(column),str(table))
        else:
            sql = "SELECT MAX({0}) FROM {1} WHERE {2}".format(str(column),str(table),where_part)
        print(sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        results = cursor.fetchall()
        return results[0][0]

    #select min of a column
    def selectmin(self,table,column):
        table = self.database_name + "." + table
        column = column[0]
        where_part = ""
        first = True
        if condition_dic != "":
            for key in condition_dic.keys():
                while "'" in key:
                    key = key.replace("'","")
                if first == True:
                    where_part = where_part + key + "='" + str(condition_dic[key]) + "'"
                    first = False
                else:
                    where_part = where_part + "," + key + "='" + str(condition_dic[key]) + "'"

        if where_part == "":
            sql = "SELECT MIN({0}) FROM {1}".format(str(column),str(table))
        else:
            sql = "SELECT MIN({0}) FROM {1} WHERE {2}".format(str(column),str(table),where_part)


        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        results = cursor.fetchall()
        return results[0][0]






if __name__ == "__main__":
    sys.exit()

