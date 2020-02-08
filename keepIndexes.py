"""
keep the designated indexes
$python keepIndexes.py -i path_to_images_and_labels -o path_to_outputs -ol 1,2,3 
"""
import os
import argparse
import shutil 


def copy_txt_img(fil_in, fil_out, extesion):
    img_in = fil_in.replace('.txt', '.' + extesion)
    img_out = fil_out.replace('.txt', '.' + extesion)
    print("in copy_txt_img testing", img_in)
    if os.path.exists(img_in):
        print("yes exist")
        shutil.copyfile(img_in, img_out)
        return True
    return False

def remove_empty_label_img(output, fil, extension):
    img_path = os.path.join(output, fil).replace('.txt', '.' + extension)
    if os.path.exists(img_path):
        os.remove(img_path)
        return True
    return False

parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i',"--input", default='input', type=str, help='path to the label and image data')
parser.add_argument('-o',"--output", default='output', type=str, help='path to the split data based on the classes')
parser.add_argument('-ol', "--origin_label",
                    default='origin_label', metavar='N', type=int, nargs='+', help='origin labels to keep')

args = parser.parse_args()
lab_img_dir = args.input
output = args.output
origin_label = args.origin_label

if output is not 'output' and not os.path.exists(output):
    print("output dir is not a dir")
    exit()

files = os.listdir(lab_img_dir)

for fil in files:
    if fil.find(".txt") > -1:
	    # print(fil)
        fil_in = os.path.join(lab_img_dir, fil)
        fil_out = os.path.join(output, fil)
        content = open(fil_in)
        content = content.readlines()
        with open(fil_out, "aw") as f:
            for line in content:
                line = line.split()
                if len(line) == 5 and int(line[0]) in origin_label:
                    # write it to the file
                    line = ' '.join(line)
                    f.write(line)
                    f.write('\n')
                else: 
                    print("found", line[0])
            f.close()
        if not copy_txt_img(fil_in, fil_out, 'jpg'):
            if not copy_txt_img(fil_in, fil_out, 'png'):
                if not copy_txt_img(fil_in, fil_out, 'JEPG'):
                    print("no image for ", fil_in)
                else:
                    print("found JEPG")
            else:
                print("fond png")
        else:
            print("found jpg")

# clean empty files
files = os.listdir(output)
for fil in files:
    if fil.find(".txt") > -1:
	file_path = os.path.join(output, fil)
        content = open(file_path)
        content = content.readlines()
        print ("line in the txt before remove", len(content))
	if len(content) == 0:
            os.remove(file_path)
            if not remove_empty_label_img(output, fil, 'jpg'):
                if not remove_empty_label_img(output, fil, 'png'):
                    if not remove_empty_label_img(output, fil, 'JPEG'):
                        print("no output image for ", os.path.join(output, fil))
                else:
                    print("found JEPG")
            else:
                print("found png")
        else:
            print("found jpg")
