'''
Purpose: This file is for creating 15 patches with random pixles on a labeled object in a RGB image: 9 patches cover 1/4 of the object 
and 6 patche covers 1/2 of the boject area.
The purpose is to create more training data for partical appreance of the object in the testing runs. 
Note that this file will only generate the patchted files as well as keeping the SAME yolo and pascal labels for some of the patches
and modify the bounding box for the cases then the patches are on the side. 
Author: sammi
Date: june-5-19
Instruction: 
$python patch_replacement_augmentation.py -o [path to save the files] -i [path of image and labels]

'''

import os
import cv2
import random
import argparse
from shutil import copyfile
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i',"--input", default='input', type=str, help='path to the label and image data')
parser.add_argument('-o',"--output", default='output', type=str, help='path to save the images labelled')

args = parser.parse_args()
INPUT_DIR = args.input
OUTPUT_DIR = args.output
print("input: ", INPUT_DIR)
print("output: ", OUTPUT_DIR)

rs_WIDTH = 424.0
rs_HEIGHT = 240.0
SMALL_AREA = 32*32


def read_yolo_annotation(file):
    content = open(file)
    labels = content.readlines()
    offset = []
    wid_hei = []
    lines = []
    for line in labels:
        print(line)
        line = line.split()
        lines.append(line)
        wid = int(float(line[3])*rs_WIDTH)
        hei = int(float(line[4])*rs_HEIGHT)
        wid_hei.append((wid, hei))
        offset.append((int(float(line[1])*rs_WIDTH-wid/2.0), int(float(line[2])*rs_HEIGHT-hei/2.0)))
    return zip(offset, wid_hei, lines)

# generate the patches location in the image
def get_patches(WIDTH, HEIGHT, OFFSET_WIDTH, OFFSET_HEIGHT):
    half_WIDTH = int(0.5*WIDTH)
    half_HEIGHT = int(0.5*HEIGHT)
    forth_WIDTH = int(0.25*WIDTH)
    forth_HEIGHT = int(0.25*HEIGHT)
    wid_hght1 = (half_HEIGHT, half_WIDTH)
    wid_hght2 = (HEIGHT, half_WIDTH)
    wid_hght3 = (half_HEIGHT, WIDTH)

    wid_heights = [wid_hght1, wid_hght2, wid_hght3]

    # 1/4 coverage
    patch_forth1 = (OFFSET_HEIGHT            , OFFSET_WIDTH)
    patch_forth2 = (OFFSET_HEIGHT            ,half_WIDTH+OFFSET_WIDTH)      
    patch_forth3 = (half_HEIGHT+OFFSET_HEIGHT, OFFSET_WIDTH)
    patch_forth4 = (half_HEIGHT+OFFSET_HEIGHT, half_WIDTH+OFFSET_WIDTH)
    patch_forth5 = (0+OFFSET_HEIGHT          ,forth_WIDTH+OFFSET_WIDTH)  
    patch_forth6 = (half_HEIGHT+OFFSET_HEIGHT, forth_WIDTH+OFFSET_WIDTH)
    patch_forth7 = (forth_HEIGHT+OFFSET_HEIGHT, 0+OFFSET_WIDTH)
    patch_forth8 = (forth_HEIGHT+OFFSET_HEIGHT, half_WIDTH+OFFSET_WIDTH)
    patch_forth9 = (forth_HEIGHT+OFFSET_HEIGHT, forth_WIDTH+OFFSET_WIDTH)


    patch_forth = [patch_forth1, patch_forth2, patch_forth3, patch_forth4,
    patch_forth5, patch_forth6, patch_forth7, patch_forth9, patch_forth8]

    # 1/2 coverage
    patch_half1 = patch_forth1
    patch_half2 = patch_forth5
    patch_half3 = patch_forth2
    patch_half4 = patch_forth1
    patch_half5 = patch_forth3
    patch_half6 = patch_forth7
    patch_half_first2 = [patch_half1, patch_half3]
    patch_half_last2 = [patch_half4, patch_half5]
    patch_half_first_middle = [patch_half2]
    patch_half_last_middle = [patch_half6]

    return wid_heights, patch_forth, patch_half_first2, patch_half_last2, patch_half_first_middle, patch_half_last_middle

# patch the area with random pixel and save the yolo and pascal label files
def patcher(patches, test_img, width_height, count):
    for patch in patches:
        img_matrix = cv2.imread(test_img)
        for i in range(patch[0], patch[0] + width_height[0]):
            for j in range(patch[1], patch[1] + width_height[1]):
                img_matrix[i, j] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        
        # save the image
        base = os.path.basename(test_img)
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".jpg")
        cv2.imwrite(dst, img_matrix)

        # copy the yolo label
        label_origin = os.path.join(INPUT_DIR, base[: base.find(".")] + ".txt")
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".txt")
        copyfile(label_origin, dst)

        # copy the pascal label
        label_origin = os.path.join(INPUT_DIR, base[: base.find(".")] + ".xml")
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".xml")
        copyfile(label_origin, dst)

        count += 1
    return count


def patcher_special(patches, test_img, width_height, count, label_line):
    print("in special")
    for k in range(len(patches)):
        patch = patches[k]
        img_matrix = cv2.imread(test_img)
        for i in range(patch[0], patch[0] + width_height[0]):
            for j in range(patch[1], patch[1] + width_height[1]):
                img_matrix[i, j] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        
        # save the image
        base = os.path.basename(test_img)
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".jpg")
        cv2.imwrite(dst, img_matrix)

        # modify the yolo label
        label_origin = os.path.join(INPUT_DIR, base[: base.find(".")] + ".txt")
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".txt")
        contents = open(label_origin)
        contents = contents.readlines()
        new_contents = []
        with open(dst, "w") as f:
            for line in contents:
                line = line.strip()
                if line == ' '.join(label_line):
                    # do something
                    # yolo: wid, hei
                    # my code is : hei, wid
                    print("k", k)
                    one = line.split()
                    one[3] = width_height[1]/rs_WIDTH
                    one[4] = width_height[0]/rs_HEIGHT
                    one[1] = patches[0][1]/rs_WIDTH + one[3]/2.0 if k == 1 else patches[1][1]/rs_WIDTH + one[3]/2.0
                    one[2] = patches[0][0]/rs_HEIGHT + one[4]/2.0 if k == 1 else patches[1][0]/rs_HEIGHT + + one[4]/2.0
                    print("here", line, one)
                    for i in range(1, len(one)):
                        one[i] = str(one[i])
                    line = ' '.join(one)
                f.write(line)
            f.close()

        # modify the pascal label
        label_origin = os.path.join(INPUT_DIR, base[: base.find(".")] + ".xml")
        tree = ET.parse(label_origin)
        root = tree.getroot()
        for xmin in root.iter('xmin'):
            text = patches[0][1] if k == 1 else patches[1][1]
            xmin.text = str(text)
        for ymin in root.iter('ymin'):
            text = patches[0][0] if k == 1 else patches[1][0]
            ymin.text = str(text)

        for xmax in root.iter('xmax'):
            text = patches[0][1] + width_height[1] if k == 1 else patches[1][1] + width_height[1] 
            xmax.text = str(text)
        for ymax in root.iter('ymax'):
            text = patches[0][0] + width_height[0]  if k == 1 else patches[1][0] + width_height[0]
            ymax.text = str(text)

        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".xml")
        tree.write(dst)
        count += 1
    return count

# deal with one image
def patch_one_img(test_img, labels):
    count = 0
    for i in range (len(labels)):   
        (OFFSET_w, OFFSET_h) = labels[i][0]
        (WIDTH, HEIGHT) = labels[i][1]
        label_lines = labels[i][2]
            
        if WIDTH*HEIGHT > SMALL_AREA:
            wid_heights, patch_forth, patch_half_first2, patch_half_last2, patch_half_first_middle, patch_half_last_middle = get_patches(WIDTH, HEIGHT, OFFSET_w, OFFSET_h)

            count = patcher(patch_forth, test_img, wid_heights[0], count)
            count = patcher(patch_half_first_middle, test_img, wid_heights[1], count)
            count = patcher(patch_half_last_middle, test_img, wid_heights[2], count)
            count = patcher_special(patch_half_first2, test_img, wid_heights[1], count, label_lines)
            count = patcher_special(patch_half_last2, test_img, wid_heights[2], count, label_lines)
             
        else:
            print("it is too small")

# deal with a folder containing image and labels
files = os.listdir(INPUT_DIR)
test_images_files = []
label_files = []
for file in files:
    print(file)
    if file.find(".jpg") > 0:
        test_images_files.append(os.path.join(INPUT_DIR, file))
    elif file.find(".txt") > 0:
        label_files.append(os.path.join(INPUT_DIR, file))

for i in range(len(test_images_files)):
    print("iiii", i)
    test_img = test_images_files[i]
    label_file = label_files[i]    
    labels = read_yolo_annotation(label_file)
    patch_one_img(test_img, labels)
