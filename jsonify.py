import re
import csv
import os
import json
import xml.etree.ElementTree as ET

def main():    
    resource_dirs = []

    # i = 0
    for root, _, files in os.walk("./"): 
        if "dublin_core.xml" in files and "contents" in files: 
            resource_dirs.append(root)

            # only do 1000 for now
            # if (i>10000): break
            # i+=1

    # data to be dumped as json
    data = dict()
    data["data"] = dict()

    num = 0
    for item_dir in resource_dirs:
        if num % 100 == 0:
            print(f"processing {num}/{len(resource_dirs)} -- {item_dir}")

        # get photos from directory, excluding thumbnails
        image_files = get_image_files(item_dir)
        # get uri from xml
        item_uri = get_uri_suffix(item_dir)

        for image_file in image_files:
            num+=1
            photo_data = dict()
            photo_id = os.path.splitext(image_file)[0]
            
            photo_data["uri_suffix"] = item_uri
            photo_data["path"] = os.path.join(item_dir, image_file)
            photo_data["features"] = []

            data["data"][photo_id] = photo_data
            

    with open("photos.json", "w") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)

        # 	write json for each:
        # "{photo_name}": {
        #   "uri_suffix": "123123" # id at the end of url 123456789/{uri_suffix}
        #	"path": "./PATH"
        #	"vec": "[a a a a a a]"
        #	}



def get_image_files(contentsDir):
    contentsPath = os.path.join(contentsDir, "contents")
    
    imageFiles = []
    with open(contentsPath) as tsvfile:
        reader = csv.reader(tsvfile, delimiter="\t")
        imageFiles = [row[0] for row in reader if "ORIGINAL" in row[1]]

    return imageFiles

# Uses SALT-provided xml files to collect useful metadata
def get_uri_suffix(folderpath):
    tree = ET.parse(f'{folderpath}/dublin_core.xml')
    root = tree.getroot()
    for child in root:
        if child.attrib['qualifier'] == 'uri':
            data_id = child.text.split('/')[-1]
    # json.dump(data, f, ensure_ascii=False, indent=4)
    return data_id


if __name__ == "__main__":
    main()

