# remove iamge in the data.txt if label.txt is empty i.e. the image has no bbox
import os
import argparse

parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i', "--data_path", default='input',
                    type=str, help='path to old.data')
parser.add_argument('-o', "--output_data_path", default='output', type=str,
                    help='path to new.data')

args = parser.parse_args()
label_path = args.data_path
new_data_path = args.output_data_path

with open(new_data_path, "w") as f:
    with open(label_path) as _file:
        labels = _file.readlines()
        for label in labels:
            print(label.replace(label[label.find('.'):], ".txt"))
            if os.stat(label.replace(label[label.find('.'):], ".txt")).st_size > 0:
                # new_data += label
                f.write(label)
                print("writing " + label)
            else:
                print("found empty line")
    _file.close()
f.close()
