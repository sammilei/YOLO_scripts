import argparse
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from colour import Color
import math


def getLenInReal(len_in_image, focal_len):
    return focal_len*OBJ_LEN/len_in_image


def readYOLOtxt(path):
    content = open(path)
    content = content.readlines()
    content = content[0].split()
    del content[0]
    return content


def keepTxt(files):
    # keep only txt
    for f in files:
        if f.endswith(".jpg") is True or f.find("DS_Store") > 0:
            files.remove(f)
    return files

def getLen(W, H, w, h):
    return (float(w)*W + float(h)*H)/2.0
    
def getLenInImage(files, path):
    lengths = []
    for txt in files:
        txt_path = os.path.join(path, txt)
        img_path = txt_path.replace(".txt", ".jpg")
        # print("img_path", img_path)

        HEIGHT, WIDTH, _ = (cv2.imread(img_path)).shape
        # print("txt_path", txt_path)
        x, y, w, h = readYOLOtxt(txt_path)

        in_image_len = getLen(WIDTH, HEIGHT, w, h)
        lengths.append(in_image_len)
    return lengths


parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-i', "--input", default='input',
                    type=str, help='path to the txt files')
parser.add_argument('-f', "--folders", default='folders',
                    type=str, help='path to the folders')

args = parser.parse_args()
folder = args.input
folders_addr = args.folders
is_multi_folders = False

if folders_addr is not 'folders':
    folders = os.listdir(folders_addr)
    is_multi_folders = True

if is_multi_folders == False:
    files = os.listdir(folder)
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    files = keepTxt(files)
    in_image_lens = getLenInImage(files, folder)

    x = range(1, len(files) + 1)
    plt.scatter(x, in_image_lens, c='b')

else:
    # for plotting
    red = Color('green')
    blue = Color('red')
    num_of_dis = 7
    colors = list(red.range_to(blue, 7))*3
    markers = ['^', 'o', 's', '*', 'x', 'd', '_']*3
    ind = 0
    max = 32
    num_of_plots = 2
    fig, axs = plt.subplots(num_of_plots)
    fig.suptitle('Len VS distance')


    means = []
    stds = []
    mins = []
    maxes = []
    OBJ_LEN = 0.6096
    one_foot = OBJ_LEN/2
    focal_len = (0.1015625*640 + 0.140625*512)/2 * 12/2
    print(focal_len)
    # distance_names = ['12ft', '15ft', '18ft', '21ft', '24ft', '27ft', '30ft']
    distances = [12*one_foot, 15*one_foot, 18*one_foot,
                 21*one_foot, 24*one_foot, 27*one_foot, 30*one_foot]*3
    distance_names = map(int, distances)
    in_image_lenss = []
    real_lenss = []
    errors = []
    for folder in folders:
        print("folder", folder)
        if folder is not ".DS_Store" and folder.find("rotated") > 0:
            files = os.listdir(os.path.join(folders_addr, folder))
            txts = keepTxt(files)
            in_image_lens = sorted(getLenInImage(
                txts, os.path.join(folders_addr, folder)))
            real_lens = []
            for in_image_len in in_image_lens:
                real_lens.append(getLenInReal(in_image_len, focal_len))
            in_image_lenss.append(in_image_lens)
            real_lenss.append(real_lens)
            x_pos = range(1, len(txts) + 1)
            x_pos = map(lambda x: x*32/len(txts), x_pos)
            # axs[0].plot(x_pos, real_lens, '-'+markers[ind], color=str(colors[ind]),
            #             markersize=5, linewidth=1,
            #             markeredgecolor=str(colors[ind]),
            #             markeredgewidth=2)
            # axs[0].set_xlabel("files")
            # axs[0].set_ylabel('len')
            ind += 1
            print("ind", ind, "max", len(txts))

            means.append(np.mean(real_lens))
            stds.append(np.std(real_lens))
            mins.append(real_lens[-1])
            maxes.append(real_lens[0])

            # errors
            error_sum = 0
            for len_ in real_lens:
                error_sum += (len_ - distances[ind - 1])**2
            error = math.sqrt(error_sum)/len(real_lens)
            print(str(distances[ind - 1]), "error:",
                  str(error))
            errors.append(error)

    x_pos = np.arange(len(distance_names))

    bp = axs[1].boxplot(real_lenss, labels=distance_names)
    axs[0].set_xlabel('Distance')
    axs[0].set_ylabel('len in image')

    print(distance_names)

    axs[1].plot(distance_names[:7], errors[:7], '-'+markers[1], color=str(colors[0]),
                markersize=5, linewidth=1,
                markeredgecolor=str(colors[0]),
                markeredgewidth=2)
    axs[1].plot(distance_names[:7], errors[7:14], '-'+markers[2], color=str(colors[3]),
                markersize=5, linewidth=1,
                markeredgecolor=str(colors[3]),
                markeredgewidth=2)
    axs[1].plot(distance_names[:7], errors[14:], '-'+markers[3], color=str(colors[13]),
                markersize=5, linewidth=1,
                markeredgecolor=str(colors[13]),
                markeredgewidth=2)

    print("real", distances)
    print("mins", mins)
    print("means", means)
    print("maxes", maxes)


plt.tight_layout()
plt.grid(b=True, which='both')
plt.show()
