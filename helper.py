from enums import *



def convert_size_to_string(filesize):
    if filesize is None:
        return "Unknown"
    if filesize >= GB:
        return str(round(filesize / GB , 2)) + " GB"
    elif filesize >= MB:
        return str(round(filesize / MB, 2)) + " MB"
    elif filesize >= KB:
        return str(round(filesize / KB, 2)) + " KB"
    else:
        return str(round(filesize / BYTE, 2)) + " Byte"
    