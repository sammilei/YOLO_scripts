'''
Purpose: ??
Author: sammi
Date: Aug-6-20
How to run: 
$python image_split.py -o [path to save the files] -i [path of image] -a patch
'''

import os
import cv2
import argparse
import numpy as np

# generate the patches location in the image


def get_patches(img_wid, img_hei, num_of_row, num_of_col):
    patch_indexes = {}  # [00: (top_y, top_x), (patch_y, patch_x))]
    patch_y = int(img_hei/num_of_row)
    patch_x = int(img_wid/num_of_col)
    for i in range(num_of_row):
        for j in range(num_of_col):
            patch_indexes[str(i) + str(j)] = [(i*patch_y,
                                               j*patch_x), (patch_y, patch_x)]
    return patch_indexes


def patch_image(patch_indexes, img_cvmat, img_wid, imd_hei, outdir, base):
    for key, pat in patch_indexes.items():
        pat_mat = img_cvmat[pat[0][0]: pat[0][0] +
                            pat[1][0], pat[0][1]:pat[0][1]+pat[1][1]]
        img_path = os.path.join(outdir, base + "_" + key + ".jpg")
        cv2.imwrite(img_path, pat_mat)
        # print("saving", img_path)


'''
stitch the imgs based on their name
'''


def get_series(img_series):
    # get series
    rows = []
    cols = []
    for img_name in img_series:
        rows.append(img_name[-6:-5])
        cols.append(img_name[-5:-4])
    num_of_row = max(list(map(int, rows)))
    num_of_col = max(list(map(int, cols)))
    return num_of_row+1, num_of_col+1


def find_patch_img(img_series, row, col):
    for img_name in img_series:
        if str(row)+str(col) in img_name[-6:]:
            return img_name
    return None


def stitch_image(img_series, outdir):
    print("in stitch")
    num_of_row, num_of_col = get_series(img_series)
    one_stitch = cv2.imread(img_series[0])
    stitch_shape = one_stitch.shape
    img_wid = stitch_shape[1] * num_of_col
    img_hei = stitch_shape[0] * num_of_row
    img_stitch = np.zeros((img_hei, img_wid, 3), np.uint8)
    for i in range(num_of_row):
        for j in range(num_of_col):
            patch_file = find_patch_img(img_series, i, j)
            img = cv2.imread(patch_file)
            hei, wid, _ = img.shape
            for pix_i in range(wid):
                for pix_j in range(hei):
                    img_stitch[i*hei+pix_j][j*wid+pix_i] = img[pix_j][pix_i]

    out_path = os.path.join(
        outdir, os.path.basename(img_series[0])[:-7] + ".jpg")
    print(out_path)
    cv2.imwrite(out_path, img_stitch)


def read_yolo_annotation(file, img_hei, img_wid):
    content = open(file)
    labels = content.readlines()
    offset = []
    hei_wid = []
    lines = []
    cls_ = []
    for line in labels:
        line = line.split()
        lines.append(line)
        wid = int(float(line[3])*img_wid)
        hei = int(float(line[4])*img_hei)
        hei_wid.append((hei, wid))
        offset.append(
            (int(float(line[2])*img_hei-hei/2.0), int(float(line[1])*img_wid-wid/2.0)))
        cls_.append(line[0])
    # offset: hei, wid
    return zip(cls_, offset, hei_wid, lines)


def PASCAL_to_YOLO(cls_, x, y, w, h, img_wid, img_hei):
    yolo_x = (x + w*0.5)/img_wid
    yolo_y = (y + h*0.5)/img_hei
    yolo_w = w/img_wid
    yolo_h = h/img_hei

    return cls_, yolo_x, yolo_y, yolo_w, yolo_h


def get_patch_index_and_ann_coordnt(ann_corn_y, ann_corn_x, pat_hei, pat_wid):
    # print("   ", ann_corn_y, ann_corn_x, pat_hei, pat_wid)
    # new corner ann index
    ind_row = ann_corn_y//pat_hei
    ind_col = ann_corn_x//pat_wid
    # new corner ann coordinates
    new_ann_top_y = ann_corn_y % pat_hei
    new_ann_top_x = ann_corn_x % pat_wid

    # print("---", ind_row, ind_col, new_ann_top_x, new_ann_top_y)
    # index(col, row), coordinate(h, w)
    return ind_col, ind_row, new_ann_top_y, new_ann_top_x


def patch_label(patch_indexes, yolo_anns, img_wid, img_hei, outdir, base):
    # print("patch_label")
    for yolo_ann in yolo_anns:
        yolo_ann = list(yolo_ann)
        ann_hei = yolo_ann[2][0]
        ann_wid = yolo_ann[2][1]
        ann_tl_y = yolo_ann[1][0]
        ann_tl_x = yolo_ann[1][1]

        ann_tr_y = yolo_ann[1][0]
        ann_tr_x = yolo_ann[1][1] + ann_wid

        ann_bl_y = yolo_ann[1][0] + ann_hei
        ann_bl_x = yolo_ann[1][1]

        ann_br_y = yolo_ann[1][0] + ann_hei
        ann_br_x = yolo_ann[1][1] + ann_wid

        pat_hei, pat_wid = list(patch_indexes.values())[0][1]

        # get 4 corners annotation
        tl_ind_col, tl_ind_row, new_ann_tl_y, new_ann_tl_x = get_patch_index_and_ann_coordnt(
            ann_tl_y, ann_tl_x, pat_hei, pat_wid)
        tr_ind_col, tr_ind_row, new_ann_tr_y, new_ann_tr_x = get_patch_index_and_ann_coordnt(
            ann_tr_y, ann_tr_x, pat_hei, pat_wid)
        bl_ind_col, bl_ind_row, new_ann_bl_y, new_ann_bl_x = get_patch_index_and_ann_coordnt(
            ann_bl_y, ann_bl_x, pat_hei, pat_wid)
        br_ind_col, br_ind_row, new_ann_br_y, new_ann_br_x = get_patch_index_and_ann_coordnt(
            ann_br_y, ann_br_x, pat_hei, pat_wid)

        # get the unique indexes
        indexes = list(set([(tl_ind_col, tl_ind_row), (tr_ind_col, tr_ind_row),
                            (bl_ind_col, bl_ind_row), (br_ind_col, br_ind_row)]))
        yolo_lines = []
        indexes.sort()
        print(base, "indexes", indexes)
        if len(indexes) == 1:
            print("1 patch")
            yolo_line = PASCAL_to_YOLO(
                yolo_ann[0], new_ann_tl_x, new_ann_tl_y, ann_wid, ann_hei, pat_wid, pat_hei)
            yolo_lines.append(((tl_ind_row, tl_ind_col), yolo_line))

        elif len(indexes) == 2:
            if indexes[0][1] == indexes[1][1]:
                print("2 hor patches")
                # left: tl
                # print("left: tl", (tl_ind_row, tl_ind_col))
                left_ann_wid = new_ann_tl_x
                yolo_line = PASCAL_to_YOLO(
                    yolo_ann[0], new_ann_tl_x, new_ann_tl_y, left_ann_wid, ann_hei, pat_wid, pat_hei)
                yolo_lines.append(((tl_ind_row, tl_ind_col), yolo_line))
                # right: tr
                # print("right: tr", (tr_ind_row, tr_ind_col))
                right_tl_x = 0
                right_tl_y = new_ann_tr_y
                right_ann_wid = new_ann_tr_x
                yolo_line = PASCAL_to_YOLO(
                    yolo_ann[0], right_tl_x, right_tl_y, right_ann_wid, ann_hei, pat_wid, pat_hei)
                yolo_lines.append(((tr_ind_row, tr_ind_col), yolo_line))
            else:
                print("2 ver patches")
                # top: tl
                # print("top: tl", (tl_ind_row, tl_ind_col))
                top_ann_hei = new_ann_tl_y
                yolo_line = PASCAL_to_YOLO(
                    yolo_ann[0], new_ann_tl_x, new_ann_tl_y, ann_wid, top_ann_hei, pat_wid, pat_hei)
                yolo_lines.append(((tl_ind_row, tl_ind_col), yolo_line))
                # bottom: bl
                # print("bottom: bl", (bl_ind_row, bl_ind_col))
                btm_tl_x = new_ann_tl_x
                btm_tl_y = 0
                btm_ann_hei = new_ann_bl_y
                yolo_line = PASCAL_to_YOLO(
                    yolo_ann[0], btm_tl_x, btm_tl_y, ann_wid, btm_ann_hei, pat_wid, pat_hei)
                yolo_lines.append(((bl_ind_row, bl_ind_col), yolo_line))
        else:
            # TODO for continuous cases, so far it will only handle 2x2
            print(">=2 patches")
            # 2 x 2
            # top left
            # print("2x2 top left")
            tl_wid = pat_wid - new_ann_tl_x
            tl_hei = pat_hei - new_ann_tl_y
            yolo_line = PASCAL_to_YOLO(
                yolo_ann[0], new_ann_tl_x, new_ann_tl_y, tl_wid, tl_hei, pat_wid, pat_hei)
            yolo_lines.append(((tl_ind_row, tl_ind_col), yolo_line))
            # top right
            # print("2x2 top right")
            tr_wid = new_ann_tr_x
            tr_hei = pat_hei - new_ann_tr_y
            tr_tl_x = 0
            tr_tl_y = new_ann_tr_y
            yolo_line = PASCAL_to_YOLO(
                yolo_ann[0], tr_tl_x, tr_tl_y, tr_wid, tr_hei, pat_wid, pat_hei)
            yolo_lines.append(((tr_ind_row, tr_ind_col), yolo_line))
            # btm left
            # print("2x2 btm left")
            bl_wid = pat_wid - new_ann_bl_x
            bl_hei = new_ann_bl_y
            bl_tl_x = new_ann_bl_x
            bl_tl_y = 0
            yolo_line = PASCAL_to_YOLO(
                yolo_ann[0], bl_tl_x, bl_tl_y, bl_wid, bl_hei, pat_wid, pat_hei)
            yolo_lines.append(((bl_ind_row, bl_ind_col), yolo_line))
            # btm right
            # print("2x2 btm right")
            br_wid = new_ann_br_x
            br_hei = new_ann_br_y
            br_tl_x = 0
            br_tl_y = 0
            yolo_line = PASCAL_to_YOLO(
                yolo_ann[0], br_tl_x, br_tl_y, br_wid, br_hei, pat_wid, pat_hei)
            yolo_lines.append(((br_ind_row, br_ind_col), yolo_line))

        # save it as a file
        for yolo_line in yolo_lines:
            path = os.path.join(outdir, base + '_' +
                                ''.join(map(str, yolo_line[0])) + ".txt")
            new_line = ' '.join(map(str, yolo_line[1]))
            my_append(path, new_line)


def my_append(path, new_line):
    if not os.path.exists(path):
        open(path, "w")
    with open(path, "r") as f:
        # for l in f:
        content = f.read()
    with open(path, "w") as f:
        f.write(content)
        if len(content) > 0:
            f.write('\n')
        f.write(new_line)
        f.close()


def stitch_label(img_wid, img_hei, label_series):
    for file in label_series:
        annotation = get_yolo_annotation(file, img_wid, img_hei)
        '''
        group rule:
            if the gap is smaller than the biggest area, group the small ones to the big
        class decision:
            if the biggest area 
        '''


if __name__ == "__main__":
    parser = argparse.ArgumentParser("add some choices")
    parser.add_argument('-i', "--input", default='input',
                        type=str, help='path to the image data')
    parser.add_argument('-o', "--output", default='output',
                        type=str, help='path to save the images')
    parser.add_argument('-a', "--action", default="patch",
                        type=str, help="patch or stitch")
    parser.add_argument('-r', "--rows", default=2,
                        type=int, help="rows to patch")

    parser.add_argument('-c', "--cols", default=3,
                        type=int, help="cols to patch")

    args = parser.parse_args()
    INPUT_DIR = args.input
    OUTPUT_DIR = args.output
    print("input: ", INPUT_DIR)
    print("output: ", OUTPUT_DIR)

    rows = args.rows
    cols = args.cols

    imgs = os.listdir(INPUT_DIR)
    if args.action == "patch":
        print("start to patch")
        out_files = os.listdir(OUTPUT_DIR)
        for f in out_files:
            path = os.path.join(OUTPUT_DIR, f)
            if not os.path.isdir(path):
                os.remove(path)
        for img in imgs:
            if img.endswith(".jpg"):
                img_path = os.path.join(INPUT_DIR, img)
                img_mat = cv2.imread(img_path)
                height, width, _ = img_mat.shape
                base = img[:-4]
                patch_indexes = get_patches(width, height, rows, cols)
                patch_image(patch_indexes, img_mat,
                            width, height, OUTPUT_DIR, base)
                # for label
                yolo_ann_file = os.path.join(INPUT_DIR, base+".txt")
                if os.path.exists(yolo_ann_file):
                    yolo_ann = read_yolo_annotation(yolo_ann_file, height, width)
                    patch_label(patch_indexes, yolo_ann, width,
                                height, OUTPUT_DIR, base)
        print("finished patching")
    elif args.action == "stitch":
        print("to start stitch")
        print("rows", rows, "cols", cols)
        stitch_files = {}
        for img in imgs:
            base = img[:-6]
            if base not in stitch_files.keys():
                stitch_files[base] = []
            stitch_files[base].append(os.path.join(INPUT_DIR, img))

        for to_stitch in stitch_files.values():
            stitch_image(to_stitch, OUTPUT_DIR)

            print("stitched", to_stitch)
        print("finished stitching")


'''
# to split
python3 split_and_stitch/stitch_or_split.py -i /media/psf/Home/Documents/JPL-Tech/artifact_reporting/Dataset/360cam/occam_VS_rs/07292020_sammiyardDark_image_label/occamRaw_occam_vs_rs_sammi_parkingLot/ -o /media/psf/Home/Documents/JPL-Tech/artifact_reporting/image_processing/split_and_stitch/split_out/ -a patch 

# to stitch

'''
