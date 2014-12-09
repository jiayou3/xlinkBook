#!/usr/bin/env python

#author: wowdd1
#mail: developergf@gmail.com
#data: 2014.12.08

import getopt
import time
import os,sys
import utils

source = ""
align_course_name = "y"
filter_keyword = ""
column_num = "2"

cell_len=92  #  cell_len >= course_num_len + 1 + course_name_len + 3
course_name_len=70
course_num_len=8
color_index=0

def usage():
    print 'usage:'
    print '-h,--help: print help message.'
    print '-i,--input: filename or dirname'
    print '-c,--column_num: from 1 to 3'
    print '-f,--filter: keyword for filter course'
    print '-a,--align: is_align_course_name'

def alignCourseName(line):
    if align_course_name == "n":
        return line   
    course_num = line[0 : line.find(" ")].strip()
    course_name = line[line.find(" ") + 1 : ].strip()

    if len(course_name) > course_name_len:
        course_name = course_name[0 : course_name_len] + "..."

    if len(course_num) < course_num_len:
        space = ""
        for i in range(1, course_num_len - len(course_num)):
            space += " "
        return course_num + space + course_name
    return line


def print_list(file_name):
    i = 0
    old_line = ""
    old_line_2 = ""
    if os.path.exists(file_name):
        f = open(file_name,'rU')
        for line in f.readlines():
            if line.lower().find(filter_keyword.lower()) == -1:
                continue

            line = line.replace("\n", "")
            i += 1
            if column_num == "3":
                if i % 3 == 0:
                    space =""
                    for j in range(1, cell_len - len(old_line_2)):
                        space += " "
                    print old_line + space + alignCourseName(line)
                    old_line_2 = ""
                    old_line = ""
                elif ((i - 1) % 3) == 0:
                    old_line = alignCourseName(line)
                else:
                    space = ""
                    for j in range(1, cell_len - len(old_line)):
                        space += " "
                    old_line_2 = alignCourseName(line)
                    old_line = old_line + space + old_line_2
            elif column_num == "2":
                if i % 2 == 0:
                    space = ""
                    for j in range(1, cell_len - len(old_line)):
                        space += " "
                    print old_line + space + alignCourseName(line)
                    old_line = ""
                else:
                    old_line = alignCourseName(line)
            else:
                print alignCourseName(line) 
    if old_line != "":
        print old_line

    if i > 0:
        if filter_keyword != "":
            print "\nTotal " + str(i) + " records cotain " + filter_keyword + ", File: " + file_name
        else:
            print "\nTotal " + str(i) + " records, File: " + file_name
    print "\n"
            

def print_dir(dir_name):
    cur_list = os.listdir(dir_name)
    for item in cur_list:
        if item.startswith("."):
            continue

        full_path = os.path.join(dir_name, item)
        if os.path.isfile(full_path):
            print_list(full_path)
        else:
            print_dir(full_path)


def main(argv):
    global source
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:c:f:a:', [])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(1)
        elif o in ('-i', '--input'):
            source = a
        elif o in ('-c', '--column_num'):
            global column_num
            column_num = a
        elif o in ('-f', '--filter'):
            global filter_keyword
            filter_keyword = str(a).strip()
        elif o in ('-a', '--align'):
            global align_course_name
            align_course_name = a
    if source == "":
        print "you must input the input file or dir"
        usage()
        return
    if os.path.isfile(source):
        print_list(source)
    else:
        print_dir(source)

if __name__ == '__main__':
    main(sys.argv)



