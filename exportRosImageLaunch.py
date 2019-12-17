import os
import argparse
import subprocess


def checkPathExist(default, filename, path):
    # check output path existence
    print("checking " + default + " " + filename, " " + path)
    if output is default:
        print("No " + filename + " path is provided")
        exit()

    if not os.path.exists(output):
        print(filename + " dir is not a dir")
        exit()


parser = argparse.ArgumentParser("add some choices")
parser.add_argument('-b', "--bag", default='bags',
                    type=str, help='path to the bags')
parser.add_argument('-o', "--output", default='output', type=str,
                    help='path to store the extracted images moved from .ros')
parser.add_argument('-n', "--name_header",
                    default='name', metavar='N', type=str, nargs='+', help='image header')
# parser.add_argument('-e', "--export",
#                     default='export', type=str, help='the path to the export.launch')

args = parser.parse_args()
bags_dir = args.bag
output = args.output
file_name_header = args.name_header
export_launch = os.path.join(os.path.curdir, "export.launch")
if not os.path.exists("./export.launch"):
    print("export launch is not found")
    exit()

checkPathExist('output', 'output', output)
checkPathExist('bags', 'bags file', bags_dir)

# check bags path existence
if bags_dir is "bags":
    print("No bags file is provided")
    exit()

if not os.path.exists(bags_dir):
    print("The bags dir does not exist")
    exit()

print(file_name_header)
if file_name_header is "name":
    print("No name headers are provided")
    exit()

# read the bag names
bags = os.listdir(bags_dir)

for bag in bags:
    print("bag:" + bag)
    # bag_dir = output + '/' + bag
    # if os.path.exists(bag_dir):
    #     bag_dir += "1"
    # os.mkdir(bag_dir)

    new_header_name = ''
    for name in file_name_header:
        if bag.find(name) > -1:
            new_header_name += name
            dot = bag.find('.')
            bag_index = bag[bag.rfind('_')+1:dot]
            new_header_name += '-' + bag_index
            break
    print("#####new_name:" + new_header_name + "####")

    # modify export.launch
    export_launch_content = open(export_launch).readlines()
    new_export_launch_content = ''
    for line in export_launch_content:
        print("line: " + line)
        # find the bag location
        bag_keyword = "args=\"-d 2 "
        end_keyword = "\"/>"
        index_of_key = line.find(bag_keyword)
        end_index = line.find(end_keyword)

        if index_of_key > -1 and end_keyword > -1:
            start_index = index_of_key + len(bag_keyword)
            print(bags_dir, " ", bag)
            line = line[:start_index] + \
                os.path.join(bags_dir, bag).replace(
                    ' ', '\\ ') + line[end_index:]
            print("new bag export line:" + line)

        # find the jpg header location
        header_keyword = "type=\"string\" value=\""
        index_of_key = line.find(header_keyword)
        end_keyword = "%04d.jpg\"/>"
        end_index = line.find(end_keyword)
        if index_of_key > -1 and end_keyword > -1:
            start_index = index_of_key + len(header_keyword)
            line = line[:start_index] + "arroyo_parking_" + new_header_name + "_" + end_keyword + line[end_index+len(end_keyword):]
            print("new header export line:" + line)

        new_export_launch_content += line

    # create the new export file
    print(new_export_launch_content)
    f = open(export_launch, "w+")
    f.write(new_export_launch_content)
    f.close()
    print("start to execute export.launch")
    print(export_launch)

    # roslaunch the new export.launch
    subprocess.call("roslaunch " + export_launch , shell=True)
    print("done. check .ros")

print("how many bags: " + str(len(bags)))
