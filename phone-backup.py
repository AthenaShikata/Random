import sys
import os
import datetime

user = 1
#user = input("Type 1 for Evan, 2 for Rob ")

current_time = datetime.datetime.now()

current_year = current_time.year
current_month = current_time.month

print(current_year,current_month)

month1 = str(current_month - 2)
month2 = str(current_month - 1)
year1 = str(current_year)
year2 = str(current_year)

if month1 == '-1':
    month1 = '11'
    month2 = '12'
    year1 = str(current_year -1)
    year2 = str(current_year -1)
elif month1 == '0':
    month1 = '12'
    year1 = str(current_year -1)

if len(month1) == 1:
    month1 = '0'+month1
if len(month2) == 1:
    month2 = '0'+month2

print(year1, month1)
print(year2, month2)

folder1 = year1+month1+'__'
folder2 = year2+month2+'__'

print(folder1)
print(folder2)
print(user)