import os
import datetime


def add_timestamp(filename):
    fnamebase,ext = os.path.splitext(filename)
    return fnamebase + "@" + datetime.datetime.now().strftime("%y%m%d%H%M") + (ext if ext else ".dat")