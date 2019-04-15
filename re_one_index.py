# change cellphone 4 to 0
import os
import argparse

parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i',"--input", default='input', type=str, help='path to the label and image data')
parser.add_argument('-o',"--output", default='output', type=str, help='path to the split data based on the classes')
parser.add_argument('-ol',"--origin_label", default='origin_label', type=int, help='origin_label')
parser.add_argument('-nl',"--new_label", default='new_label', type=int, help='new_label')


args = parser.parse_args()
lab_img_dir = args.input
output = args.output
origin_label = str(args.origin_label)
new_label = str(args.new_label)

if output is not 'output' and not os.path.exists(output):
    print("output dir is not a dir")
    exit()

files = os.listdir(lab_img_dir)


for fil in files:
    if fil.find(".txt") > -1:
	print(fil)
        content = open(os.path.join(lab_img_dir, fil))
        content = content.readlines()
        for line in content:
            line = line.split()
            if len(line) == 5 and line[0] is origin_label:
                line[0] = new_label

                # write it to the file
                with open(os.path.join(output, fil), "w") as f:
                    line = ' '.join(line)
                    f.write(line)
                    f.close()
