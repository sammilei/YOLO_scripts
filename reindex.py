# change cellphone 4 to 0
# $ python3 re_one_index.py -i /media/psf/Home/Downloads/arroyo_parking_4resolution/1920_1080/image/d -o /media/psf/Home/Downloads/arroyo_parking_4resolution/1920_1080/image/d -ol 1 2 3 -nl 0 1 2
import os
import argparse

parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i', "--input", default='input',
                    type=str, help='path to the label and image data')
parser.add_argument('-o', "--output", default='output', type=str,
                    help='path to the split data based on the classes')
parser.add_argument('-ol', "--origin_label",
                    default='origin_label', metavar='N',type=int, nargs='+', help='origin_label')
parser.add_argument('-nl', "--new_label",
                    default='new_label', metavar='N', type=int, nargs='+', help='new_label')


args = parser.parse_args()
lab_img_dir = args.input
output = args.output
origin_label = args.origin_label
new_label = args.new_label

ol_nl = dict(zip(origin_label, new_label))
print(ol_nl)

if output is not 'output' and not os.path.exists(output):
    print("output dir is not a dir")
    exit()

files = os.listdir(lab_img_dir)

for fil in files:
    if fil.find(".txt") > -1:
        content = open(os.path.join(lab_img_dir, fil))
        content = content.readlines()
        count = 0
        with open(os.path.join(output, fil), "w") as f:
            for line in content:
                line = line.replace('\x00', '')
                line = line.split()
                if len(line) == 5 and int(line[0]) in ol_nl.keys():
                    if fil.find("a97.txt") > -1:
                        print("found it")

                    line[0] = str(ol_nl[int(line[0])])

            # write it to the file
                line = ' '.join(line)
                f.write(line)
                count =+ 1
                if count < len(content):
                    f.write('\n')
            f.close()
            count = 0
