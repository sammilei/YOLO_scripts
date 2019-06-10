'''
$python extract_phone_img_label.py -i /media/psf/Downloads/june_4_9_sets_including_huskyonline_corrected/8_STIX_artifacts_images_handheld_v2_image_and_labels/ 
-o ~/Documents/to_delete/phone/8_STIX_artifacts_images_handheld_v2_image_and_labels_phone/ -ol 4
'''

import os
import argparse
from shutil import copyfile


parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i',"--input", default='input', type=str, help='path to the label and image data')
parser.add_argument('-o',"--output", default='output', type=str, help='path to the split data based on the classes')
parser.add_argument('-ol',"--origin_label", default='origin_label', type=int, help='origin_label')


args = parser.parse_args()
INPUT_DIR = args.input
OUTPUT_DIR = args.output
origin_label = str(args.origin_label)

files = os.listdir(INPUT_DIR)

for fil in files:
    if fil.find(".txt") > -1:
        content = open(os.path.join(INPUT_DIR, fil))
        content = content.readlines()
        for line in content:
            line = line.split()
            if len(line) == 5 and line[0] is origin_label:
                base = os.path.basename(fil)
                base = base[: base.find(".")]
                # save the image
                img = os.path.join(INPUT_DIR, base + ".jpg")
                dst = os.path.join(OUTPUT_DIR, base + ".jpg")
                copyfile(img, dst)

                # copy the yolo label
                label_origin = os.path.join(INPUT_DIR, fil)
                dst = os.path.join(OUTPUT_DIR, base + ".txt")
                copyfile(label_origin, dst)

                # copy the pascal label
                label_origin = os.path.join(INPUT_DIR, base + ".xml")
                dst = os.path.join(OUTPUT_DIR, base + ".xml")
                copyfile(label_origin, dst)
                print("copied", base)

		            
