# statistic for the labels and can copy it over
# how to run 
'''
$python3 training_ds_stat.py -dir ~/Desktop/ParallelsSharedFolders/YOLO/Dataset/MarsYard/labelled/bright+dark/marsyard_030919_rs_dark -class fire_x backpack drill survivor cellphone
'''
import os
import sys
import argparse
from shutil import copyfile


parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i',"--input", default='input', type=str, help='path to the label and image data')
parser.add_argument('-class', '--classes', metavar='N', type=str, nargs='+', help='class list')
parser.add_argument('-o',"--output", default='output', type=str, help='path to the split data based on the classes')

args = parser.parse_args()

artifacts = args.classes
#artifacts = ["fire_x", "backpack", "drill", "survivor", "cellphone"]

input_dir = args.input
output_dir = args.output
print("input: ", input_dir)
print("output: ", output_dir)

''' verify the output path '''
copy_over = False
if output_dir is not 'output' and not os.path.exists(output_dir):
    print("output dir is not a dir")
    exit()
else:
    copy_over = True

files = os.listdir(input_dir)
print(copy_over)
sums = {}

file_counts = 0
print(" **** files with 1+ objects ****")
for _file in files:
    base = _file[:_file.find('.')]
    # check if txt has corresponding jpg or png
    if _file.endswith(".txt") and _file.lower().find("readme") == -1 \
    and (base + ".jpg" in files or base + ".png" in files):
        txt_src = os.path.join(input_dir, _file)
        with open(txt_src, 'r') as f:
            content = f.readlines()
            if(len(content) > 1):
                print(_file, end=' ')
            for line in content:
                # increase by 1 to the class list
                sums[int(line[0])] = sums.get(int(line[0]), 0) + 1
                if copy_over is True:
                    # check if the dir of class exists
                    if len(artifacts) > int(line[0]):
                        class_dir = os.path.join(output_dir, artifacts[int(line[0])])
                    else: 
                        class_dir = os.path.join(output_dir, "unknownClass_" + line[0])    
                    if not os.path.exists(class_dir):
                        os.mkdir(class_dir)
                        print("created a new class dir:", class_dir)
                    # copy txt
                    txt_dst = os.path.join(class_dir, _file)
                    copyfile(txt_src, txt_dst)
                    # copy img
                    img_src = txt_src.replace(".txt" ,".jpg")
                    img_dst = txt_dst.replace(".txt", ".jpg")
                    copyfile(img_src, img_dst)
                    # copy xml    
                    xml_src = txt_src.replace(".txt", ".xml")
                    if os.path.isfile(xml_src):
                        xml_dst = txt_dst.replace(".txt", ".xml")
                        copyfile(xml_src, xml_dst)
            file_counts += 1
print("\n\n# of files with label and cooridinating jpg/png: \n" + str(file_counts))


'''stat'''
sum_all = sum(sums.values())

''' printing '''
print("\nAll exist labels and counts:")
for _sum in sums.items():
    print('%d: %d - %2.2f%%' % (_sum[0], _sum[1], _sum[1]*100.0/sum_all))
print("total: " + str(sum_all))

if artifacts is not None:
    max_len = len(max(artifacts, key=len))
    print("\nWith given class names: ")
    for _sum in sums.items():
        width = max_len
        if len(artifacts) > _sum[0]:
            print('%*s: %d - %2.2f%%' % (width, artifacts[_sum[0]], _sum[1], _sum[1]*100.0/sum_all))
        else:
            print('%*s: %d - %2.2f%%' % (width, "unknownClass_" + str(_sum[0]), _sum[1], _sum[1]*100.0/sum_all))
    print("%*s: %d" %(width, 'total', sum_all))
