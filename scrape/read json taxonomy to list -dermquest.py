import json
import os
import shutil
import re
import requests
from requests import get
import time
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException


# Path to the HTML
with open("C:/Users/boman/Desktop/Dermatology Image Library - Images for Dermatologists - DermQuest.html") as html_file:
 soup = BeautifulSoup(html_file, 'html.parser')

# Path to images you want to go through
pathJson = 'C:/Users/boman/diagnostics/taxonomy.json'
# Path to where you want the list
txtFilePath = 'C:/Users/boman/Desktop/taxonomyListDermQuest.txt'

with open(pathJson) as data_file:
 jsonList = json.load(data_file)
 file = open(txtFilePath, "w")

 for trainingLabels in jsonList['children']:
     file.write("------------------------ ")
     for trainingLabelsName in trainingLabels['name'][:-1]:
         file.write(trainingLabelsName)
         file.write(" ");
     file.write(trainingLabels['name'][-1])
     file.write("\n")

     for trainingLabelsChild in trainingLabels['children']:
         file.write("++++ ")
         trainingLabelsChildNameSUM = ""
         for trainingLabelsChildName in trainingLabelsChild['name'][:-1]:
             file.write(trainingLabelsChildName)
             if trainingLabelsChildNameSUM == "":
                 trainingLabelsChildNameSUM += trainingLabelsChildName.title()
             else:
                 trainingLabelsChildNameSUM = trainingLabelsChildNameSUM + " " + trainingLabelsChildName.title()
             file.write(" ");
         file.write(trainingLabelsChild['name'][-1])
         if trainingLabelsChildNameSUM == "":
             trainingLabelsChildNameSUM += trainingLabelsChild['name'][-1].title()
         else:
             trainingLabelsChildNameSUM += " " + trainingLabelsChild['name'][-1].title()

         find_string1 = soup.body.findAll(text=trainingLabelsChildNameSUM)
         file.write(" ")
         if len(find_string1) < 1:
             file.write("NO")
         else:
             file.write("YES")
             file.write(" ")
             file.write("ID: ")
             file.write(find_string1[0].parent.attrs['for'])
         file.write("\n")

         for trainingLabelsGrandChild in trainingLabelsChild['children']:
             file.write("** ")
             trainingLabelsGrandChildNameSUM = ""
             for trainingLabelsGrandChildName in trainingLabelsGrandChild['name'][:-1]:
                 file.write(trainingLabelsGrandChildName)
                 if trainingLabelsGrandChildNameSUM == "":
                     trainingLabelsGrandChildNameSUM += trainingLabelsGrandChildName.title()
                 else:
                     trainingLabelsGrandChildNameSUM = trainingLabelsGrandChildNameSUM + " " + trainingLabelsGrandChildName.title()
                 file.write(" ");

             file.write(trainingLabelsGrandChild['name'][-1])
             if trainingLabelsGrandChildNameSUM == "":
                 trainingLabelsGrandChildNameSUM += trainingLabelsGrandChild['name'][-1].title()
             else:
                 trainingLabelsGrandChildNameSUM = trainingLabelsGrandChildNameSUM + " " + trainingLabelsGrandChild['name'][-1].title()

             find_string = soup.body.findAll(text=trainingLabelsGrandChildNameSUM)
             file.write(" ");
             if len(find_string) < 1:
                 file.write("NO")
             else:
                 if not find_string[0] == " ":
                     file.write("YES")
                     file.write(" ");
                     file.write("ID: ")
                     file.write(find_string[0].parent.attrs['for'])
             file.write("\n")
         file.write("\n")
     file.write("\n")



 file.close()
 data_file.close()

html_file.close()


print("DONE!")
