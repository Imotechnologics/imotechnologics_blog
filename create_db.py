# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 16:24:12 2023

@author: dvildmonpsy
"""
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Bombaz.542",
    )

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)