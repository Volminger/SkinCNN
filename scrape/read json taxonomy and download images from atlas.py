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

def scrapeImagesForDiagnosis (diseasePage, folder_to_save_in):
    if not os.path.exists(folder_to_save_in):
        os.makedirs(folder_to_save_in)

    driver = webdriver.Chrome('C:/Users/boman/Downloads/chromedriver_win32/chromedriver.exe')
    driver.get(diseasePage)
    # Wait for images to load
    time.sleep(5)
    driver.execute_script("window.scrollTo(0,0);")
    time.sleep(1)

    count = 0
    # Select folder to save in
    file_name_origin = folder_to_save_in + '/Atlas'

    images = driver.find_elements_by_tag_name('img')
    for image in images:
        src = image.get_attribute("src")
        if src and 'thumb' in src:
            count += 1
            file_name = file_name_origin + str(count) + ".jpg"
            with open(file_name, "wb") as file:
                # get request

                response = get(src)
                # write to file
                file.write(response.content)

    driver.close()
    print("DONE!")

#scrapeImagesForDiagnosis('facet_109891', 'E:/KEX/DermQuestTestDownload/Melanoma')

# Path to the HTML
with open("C:/Users/boman/Desktop/Browse _ Dermatology Atlas.html") as html_file:
 soup = BeautifulSoup(html_file, 'html.parser')

# Path to images you want to go through
pathJson = 'C:/Users/boman/diagnostics/taxonomy.json'
# Path to where you want to save the images
imageSavingPath = 'E:/KEX/AtlasTestDownload'

with open(pathJson) as data_file:
 jsonList = json.load(data_file)

 for trainingLabels in jsonList['children']:
     imageSavingPathLevel1 = imageSavingPath + "/"
     #file.write("---- ")
     for trainingLabelsName in trainingLabels['name'][:-1]:
         imageSavingPathLevel1 += trainingLabelsName
         imageSavingPathLevel1 += " "
     imageSavingPathLevel1 += trainingLabels['name'][-1]
     if not os.path.exists(imageSavingPathLevel1):
         os.makedirs(imageSavingPathLevel1)

     for trainingLabelsChild in trainingLabels['children']:
         #file.write("++++ ")
         imageSavingPathLevel2 = imageSavingPathLevel1 + '/'
         trainingLabelsChildNameSUM = ""
         for trainingLabelsChildName in trainingLabelsChild['name']:
             if trainingLabelsChildNameSUM == "":
                 trainingLabelsChildNameSUM += trainingLabelsChildName
             else:
                 trainingLabelsChildNameSUM += " " + trainingLabelsChildName

         print(trainingLabelsChildNameSUM)
         find_string1 = soup.body.findAll(text=trainingLabelsChildNameSUM)
         if not len(find_string1) < 1:
             #file.write("YES")
             #file.write("ID: ")
             #file.write(find_string1[0].parent.attrs['for'])
             imageSavingPathLevel2 += trainingLabelsChildNameSUM
             if not os.path.exists(imageSavingPathLevel2):
                 os.makedirs(imageSavingPathLevel2)
             else: continue
             scrapeImagesForDiagnosis(find_string1[0].parent.attrs['href'], imageSavingPathLevel2)


         for trainingLabelsGrandChild in trainingLabelsChild['children']:
             #file.write("** ")
             imageSavingPathLevel3 = imageSavingPathLevel2 + '/'
             trainingLabelsGrandChildNameSUM = ""
             for trainingLabelsGrandChildName in trainingLabelsGrandChild['name']:
                 if trainingLabelsGrandChildNameSUM == "":
                     trainingLabelsGrandChildNameSUM += trainingLabelsGrandChildName
                 else:
                     trainingLabelsGrandChildNameSUM += " " + trainingLabelsGrandChildName

             print(trainingLabelsGrandChildNameSUM)
             find_string = soup.body.findAll(text=trainingLabelsGrandChildNameSUM)
             if not len(find_string) < 1:
                 if not find_string[0] == " ":
                     #file.write("YES")
                     #file.write("ID: ")
                     #file.write(find_string[0].parent.attrs['for'])
                     imageSavingPathLevel3 += trainingLabelsGrandChildNameSUM
                     if not os.path.exists(imageSavingPathLevel3):
                         os.makedirs(imageSavingPathLevel3)
                     else: continue
                     scrapeImagesForDiagnosis(find_string[0].parent.attrs['href'], imageSavingPathLevel3)

 data_file.close()

html_file.close()
print("All downloads complete!!!")
