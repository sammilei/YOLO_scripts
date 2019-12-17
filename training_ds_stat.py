# statistic for the labels and can copy it over for a folder or data.txt
# how to run
'''
$python3 training_ds_stat.py -i ~/Desktop/ParallelsSharedFolders/YOLO/Dataset/MarsYard/labelled/bright+dark/marsyard_030919_rs_dark -class fire_x backpack drill survivor cellphone
'''
import os
import sys
import argparse
from shutil import copyfile


parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i', "--input", default='input',
                    type=str, help='path to the label and image data')
parser.add_argument('-class', '--classes', metavar='N',
                    type=str, nargs='+', help='class list')
parser.add_argument('-o', "--output", default='output', type=str,
                    help='path to the split data based on the classes')

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
elif output_dir is not 'output':
    copy_over = True

# get the labels
# if is a data.txt containing .jpg/png/JPEG
if input_dir.find('.txt') > -1:
    lables_file = open(input_dir, 'r')
    files = lables_file.readlines()
    files = [file_[:file_.rfind('.')] + '.txt' for file_ in files if file_.find(
        '.jpg') or file_.find('.png') or file_.find('.JPEG')]
    if len(files) == 0:
        print("no JPG or PNG or JPEG is found in the .txt")
        exit()
# if a dir containing bbox.txt and img.jpg/png/JPEG
elif os.path.isdir(input_dir):
    files = os.listdir(input_dir)
    files = [os.path.join(input_dir, file_)
             for file_ in files if file_.endswith('.txt')]
else:
    print("input is not a .txt or a directory")
    exit()
sums = {}

file_counts = 0
print(" **** files with 1+ objects ****")
for _file in files:
    jpg_path = _file.replace('.txt', '.jpg')
    png_path = _file.replace('.txt', '.png')
    if os.path.exists(jpg_path) or os.path.exists(png_path):
        with open(_file, 'r') as f:
            content = f.readlines()
            for line in content:
                # increase by 1 to the class list
                line = line.replace('\x00', '')
                sums[int(line[0])] = sums.get(int(line[0]), 0) + 1
                if copy_over is True:
                    # check if the dir of class exists
                    if len(artifacts) > int(line[0]):
                        class_dir = os.path.join(
                            output_dir, line[0] + "_" + artifacts[int(line[0])])
                    else:
                        class_dir = os.path.join(
                            output_dir, "unknownClass_" + line[0])
                    if not os.path.exists(class_dir):
                        os.mkdir(class_dir)
                        print("created a new class dir:", class_dir)
                    # copy txt
                    txt_dst = os.path.join(class_dir, _file)
                    copyfile(txt_src, txt_dst)
                    # copy img
                    img_src = txt_src.replace(".txt", ".jpg")
                    img_dst = txt_dst.replace(".txt", ".jpg")
                    copyfile(img_src, img_dst)
                    # copy xml
                    xml_src = txt_src.replace(".txt", ".xml")
                    if os.path.isfile(xml_src):
                        xml_dst = txt_dst.replace(".txt", ".xml")
                        copyfile(xml_src, xml_dst)
            file_counts += 1
    else:
        print("can't find png or jpg for ", _file)
        exit()
print("\n\n# of files with label and cooridinating jpg/png: \n" + str(file_counts))


'''stat'''
sum_all = sum(sums.values())

''' printing '''
print("\nAll exist labels and counts:")
sorted_sum = sorted(sums.items(), key=lambda x: x[0])
for _sum in sorted_sum:
    print('%d: %d - %2.2f%%' % (_sum[0], _sum[1], _sum[1]*100.0/sum_all))
print("total: " + str(sum_all))

if artifacts is not None:
    max_len = len(max(artifacts, key=len))
    width = 0
    print("\nWith given class names: ")
    for _sum in sums.items():
        width = max_len
        if len(artifacts) > _sum[0]:
            print('%*s: %d - %2.2f%%' %
                  (width, artifacts[_sum[0]], _sum[1], _sum[1]*100.0/sum_all))
        else:
            print('%*s: %d - %2.2f%%' % (width, "unknownClass_" +
                                         str(_sum[0]), _sum[1], _sum[1]*100.0/sum_all))
    print("%*s: %d" % (width, 'total', sum_all))
