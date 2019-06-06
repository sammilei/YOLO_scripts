'''
Purpose: This file is for creating 15 patches with random pixles on a labeled object in a RGB image: 9 patches cover 1/4 of the object 
and 6 patche covers 1/2 of the boject area.
The purpose is to create more training data for partical appreance of the object in the testing runs. 
Note that this file will only generate the patchted files as well as keeping the SAME yolo and pascal labels. 
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

parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i',"--input", default='input', type=str, help='path to the label and image data')
parser.add_argument('-o',"--output", default='output', type=str, help='path to save the images labelled')

args = parser.parse_args()
INPUT_DIR = args.input
OUTPUT_DIR = args.output
print("input: ", INPUT_DIR)
print("output: ", OUTPUT_DIR)

rs_WIDTH = 424
rs_HEIGHT = 240
SMALL_AREA = 32*32


def read_yolo_annotation(file):
    content = open(file)
    labels = content.readlines()
    offset = []
    wid_hei = []
    for line in labels:
        print(line)
        line = line.split()
        wid = int(float(line[3])*rs_WIDTH)
        hei = int(float(line[4])*rs_HEIGHT)
        wid_hei.append((wid, hei))
        offset.append((int(float(line[1])*rs_WIDTH)-wid/2, int(float(line[2])*rs_HEIGHT)-hei/2))

        print("offset", offset, "wid height", wid_hei)
    return zip(offset, wid_hei)

# generate the patches location in the image
def get_patches(WIDTH, HEIGHT, OFFSET_WIDTH, OFFSET_HEIGHT):
    half_WIDTH = int(0.5*WIDTH)
    half_HEIGHT = int(0.5 * HEIGHT)
    forth_WIDTH = int(0.25 * WIDTH)
    forth_HEIGHT = int(0.25 * HEIGHT)
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
    patch_half_first3 = [patch_half1, patch_half2, patch_half3]
    patch_half_last3 = [patch_half4, patch_half6, patch_half5]

    return wid_heights, patch_forth, patch_half_first3, patch_half_last3

# patch the area with random pixel and save the yolo and pascal label files
def patcher(patches, test_img, width_height, count):
    for path in patches:
        img_matrix = cv2.imread(test_img)
        for i in range(path[0], path[0] + width_height[0]):
            for j in range(path[1], path[1] + width_height[1]):
                img_matrix[i, j] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        
        # save the image
        base = os.path.basename(test_img)
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".jpg")
        cv2.imwrite(dst, img_matrix)

        # copy the yolo label
        label_origin = os.path.join(INPUT_DIR, base[: base.find(".")] + ".txt")
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".txt")
        copyfile(label_origin, dst)

        # copy the yolo label
        label_origin = os.path.join(INPUT_DIR, base[: base.find(".")] + ".xml")
        dst = os.path.join(OUTPUT_DIR, base[: base.find(".")] + "_" + str(count) + ".xml")
        copyfile(label_origin, dst)

        count += 1
    return count

# deal with one image
def patch_one_img(test_img, labels):
    count = 0
    for i in range (len(labels)):   
        print("label", labels[i])     
        (OFFSET_w, OFFSET_h) = labels[i][0]
        (WIDTH, HEIGHT) = labels[i][1]
            
        if WIDTH*HEIGHT > SMALL_AREA:
            wid_heights, patch_forth, patch_half_first3, patch_half_last3 = get_patches(WIDTH, HEIGHT, OFFSET_w, OFFSET_h)

            count = patcher(patch_forth, test_img, wid_heights[0], count)
            count = patcher(patch_half_first3, test_img, wid_heights[1], count)
            patcher(patch_half_last3, test_img, wid_heights[2], count) 
        else:
            print("it is too small")

# deal with a folder containing image and labels
files = os.listdir(INPUT_DIR)
test_images_files = []
label_files = []
for file in files:
    print(file
    if file.find(".jpg") > 0:
        test_images_files.append(os.path.join(INPUT_DIR, file))
    elif file.find(".txt") > 0:
        label_files.append(os.path.join(INPUT_DIR, file))

for i in range(len(test_images_files)):
    test_img = test_images_files[i]
    label_file = label_files[i]    
    labels = read_yolo_annotation(label_file)
    patch_one_img(test_img, labels)
