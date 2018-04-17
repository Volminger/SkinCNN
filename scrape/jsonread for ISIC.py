import json
import os
import shutil

count = 1

# Path to images you want to go through
path = 'C:/Users/boman/ISIC-images'
# Path to where you want the images
finalPath = 'C:/Users/boman/Lesion-images'

for root, dirs, files in os.walk(path):
 for name in files:
  if name.endswith(".json"):
   src = root + '/' + name
   with open(src) as data_file:
    jsonList = json.load(data_file)

    disease = jsonList['meta']['clinical']['diagnosis']
    imageSrcPath = root + '/' + jsonList['name'] + '.jpg'
    diseaseDir = finalPath + '/' + disease
    if not os.path.exists(diseaseDir):
     os.makedirs(diseaseDir)

    data_file.close()
    shutil.copy2(imageSrcPath, diseaseDir)


print("DONE!")
