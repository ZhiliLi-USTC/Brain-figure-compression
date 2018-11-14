#!/usr/bin/python3
#** encoding UTF-8 **#
import subprocess
import time
import math
import glob
import os
import shutil
import processing
import PSNR


def compress(path_origin_tiff, path_mkv, crf, lossless):
    """
    This function calls external programs ffmpeg.exe and use it to compress tiff files in a folder.
    Args:
        path_origin_tiff:the path of the 16bits tiff folder,and the tiff file name in the folder should be 0_0_%d.tiff.
        path_mkv:the path of the output mkv file
        crf:one parameter in H.265 coding standard,it ranges from 0 to 51
        lossless:if lossless equals 1,the compression will be lossless regardless the value of crf
    Return:It return a dictionary of the compression.The first component is the number of the encoded frames,
    the second one is compression time,and the last one is the average QP.
    """
    command ='ffmpeg -f image2 -start_number 30 -i ' + path_origin_tiff + '\\0_0_%d.tiff  ' \
           '-vcodec libx265 -y -preset ultrafast '
    if lossless == 1:
        command = command + ' -x265-params lossless=1 ' + path_mkv
    else:
        command = command + ' -x265-params crf=' + str(crf) + ' ' +  path_mkv
    ret = subprocess.Popen(command, stderr=subprocess.PIPE)  #ret is the ffmpeg run information and its type is bytes
    string = bytes.decode(ret.stderr.read())  #convert the ffmpeg run information to string
    ret.communicate()
    # get the last line of the run information which is the key information of the compression
    end_line = string.split('\r\n')[-2]
    dic = {}
    #get the "encoded frames","Compress time(s)" and "Avg QP" from the last line
    dic['Encoded frames'] = end_line.split()[1]
    dic['Compress time(s)'] = end_line.split()[4][0:-2]
    dic['Avg QP'] = end_line.split()[-1].split(':')[-1]
    return dic

def decompress(path_mkv, path_decompress_tiff):
    """
    This function calls external programs ffmpeg.exe and use it to decompress a mkv file to tiff files.
    Args:
        path_mkv:the input mkv file path
        path_decompress_tiff:the output tiff file path,it should be a folder
    Return:It returns the decompression time,and the unit is second.
    """
    command = 'ffmpeg -i ' + path_mkv + ' -start_number 30 ' + path_decompress_tiff + '\\' + '0_0_%d.tiff -preset ultrafast'
    start = time.clock()   #start the timer
    ret = subprocess.Popen(command, stderr=subprocess.PIPE)
    bytes.decode(ret.stderr.read())
    ret.communicate()
    end = time.clock()  #end the timer
    decompress_time=end-start   #get the decompression time
    return decompress_time

def get_cmd_from_user():
    """
    This function interacts with the user, and get compression command and file path from the user.
    """
    path_tiff = input("Please input the origin tiff folder's path:")
    tiff_file = glob.glob(path_tiff + '\\' + '*.tiff')
    if len(tiff_file) == 0:
        print('Error: No tiff file in this folder\nPlease check the input tiff path.')
        return
    path_mkv = input("Please input the output mkv path:")
    if not os.path.exists(path_mkv):
        print('folder {folder} is created!'.format(folder=path_mkv))
        makdir(path_mkv)
    params = input("Please input the compress ratio minimum and the PSNR minimum(use space split): ")
    try:
        compress_ratio_total_minimum = int(params.split()[0])
        psnr_minimum = int(params.split()[1])
        if compress_ratio_total_minimum <= 0:
            print("Compression ratio should be a positive number. ")
            return
        if psnr_minimum <= 0:
            print("PSNR minimum should be a positive number.")
    except ValueError:
        print("Could not convert input data to an integer.")
        return
    except IndexError:
        print("Ensure you have input two parameters.")
        return
    except Exception as e:
        print(e)
        return
    path_decompress_tiff = input("please input the decompress tiff path:")
    path_split_list = processing.tiff_split(path_tiff, path_mkv)

    #this is for debug
    #compress_ratio_total_minimum = 100
    #psnr_minimum = 36
    #path_mkv = "D:\study\Ometiff\\test"
    #path_decompress_tiff = "D:\study\Ometiff\\test\decompress"
    #path_split_list = ["D:\study\Ometiff\\test\high8bits", "D:\study\Ometiff\\test\low8bits"]

    #compress the high 8 bits tiff files to a mkv losslessly
    dic_high = compress(path_split_list[0], path_mkv + '\\' + 'high_lossless.mkv', 0, 1)
    #get the mkv file size compressed from the high 8 bits tiff file
    high_mkv_size = os.path.getsize(path_mkv + '\\' + 'high_lossless.mkv') / float(1024 * 1024)
    #get the total size of the origin high 8 bits tiff files
    size_high8bits = get_folder_size(path_split_list[0])
    #get the total size of the origin low 8 bits tiff files
    size_low8bits = get_folder_size(path_split_list[1])
    #compute the low 8bits tiff file compression ratio according to the total compression ratio
    compress_ratio_low_minimum = size_low8bits / ((size_high8bits + size_low8bits) / compress_ratio_total_minimum -
                                                  high_mkv_size)
    # find the crf bottom value that meets the compression ratio requirement
    crf_bottom = find_bottom_crf(path_split_list, path_mkv, compress_ratio=compress_ratio_low_minimum)
    #find the crf top value that meets the psnr requirement
    crf_top = find_top_crf(path_split_list, path_mkv, psnr_minimum=psnr_minimum)
    #if the crf bottom value is bigger than crf top value,then the program will terminate
    if crf_bottom[0] > crf_top[0]:
        print("No crf meets the requirements!")
        return
    #print available crf value and relative information
    print('the crf interval that meets the requirements is:[{bottom},{top}]'
          .format(bottom=crf_bottom[0], top=crf_top[0]))
    print('\ncrf={bottom}\ncompression information:{compress}\ndecompression time: {time}s\ncompression'
          ' ratio:{ratio}\npsnr:{psnr}'.format(bottom=crf_bottom[0], compress=crf_bottom[1], time=crf_bottom[2],
            ratio=(size_low8bits + size_high8bits) / (high_mkv_size + crf_bottom[3]), psnr=crf_bottom[4]))
    print('\ncrf={top}\ncompression information:{compress}\ndecompression time: {time}s\ncompression'
          ' ratio:{ratio}\npsnr:{psnr}'.format(top=crf_top[0], compress=crf_top[1], time=crf_top[2],
            ratio=(size_low8bits + size_high8bits) / (high_mkv_size + crf_top[3]), psnr=crf_top[4]))
    #ask the user to give a specific crf value to compress
    try:
        crf_user = int(input("\nplease choose a crf value from the optional crf interval:"))
        if crf_user < 0 or crf_user > 51:
            print("Crf value is invalid.")
            return
    except ValueError:
        print("Please input a integer.")
        return
    except Exception as e:
        print(e)
        return
    dic_low = compress(path_split_list[1], path_mkv + '\\' + 'low_' + str(crf_user) +'.mkv', crf_user, 0)
    low_mkv_size = os.path.getsize(path_mkv + '\\' + 'low_' + str(crf_user) +'.mkv') / float(1024 * 1024)
    #print the compression information
    print("\nhigh8bits compression:{high}\nlow8bits compression:{low}:".format(high=dic_high, low=dic_low))
    print("compression ratio:high {high},low {low},total {total}".format(high=size_high8bits / high_mkv_size,
          low=size_low8bits / low_mkv_size, total=(size_low8bits + size_high8bits) / (low_mkv_size + high_mkv_size)))
    path_dec_high = path_decompress_tiff + '\\' + 'high_decompress'
    path_dec_low = path_decompress_tiff + '\\' + 'low_decompress'
    path_dec_merge = path_decompress_tiff + '\\' + 'merge'
    makdir(path_dec_high)
    makdir(path_dec_low)
    makdir(path_dec_merge)
    #decompress
    dec_low_time = decompress(path_mkv + '\\' + 'low_' + str(crf_user) + '.mkv', path_dec_low)
    dec_high_time = decompress(path_mkv + '\\' + 'high_lossless.mkv', path_dec_high)
    print("decompression time:high {htime}s,low {ltime}s".format(htime=dec_high_time, ltime=dec_low_time))
    #compute the psnr and print
    psnr_class = PSNR.compute_psnr()
    psnr = psnr_class.tiff_psnr(path_dec_low, path_split_list[1], 8)
    print("low8bits psnr:{psnr}dB".format(psnr=psnr))
    print("total psnr:{psnrtotal}dB".format(psnrtotal=psnr + 20 * math.log10(65535 / 255)))
    #merge the decompress 8 bits tiff files to 16bits files
    processing.tiff_merge(path_dec_high, path_dec_low, path_dec_merge, 30, 848)



def find_top_crf(path_split_list, path_mkv, psnr_minimum):
    """
    This function can find the top crf value that meets the psnr requirements.
    Args:
        path_split_list: the list whose components are the high8bits and low8bits tiff folder path
        path_mkv: a path that save the temp mkv file
        psnr_minimum:the minimum psnr value
    Return:It returns the top crf value,compression information,decompression time,  the mkv file size and psnr.
    """
    step = 16
    psnr_class = PSNR.compute_psnr()
    crf_begin = 51
    crf_end = 0
    dic_compress = []
    time_decompress = []
    size_mkv = []
    psnr = []
    record_dic = {}
    path_tmp = path_mkv + '\\' + 'tmp'
    makdir(path_tmp)
    #this module can find the top crf value that meets the psnr requirement by decreasing the step size gradually
    while step > 0:
        for crf in range(crf_begin, crf_end - 1, -1 * step):
            if crf not in record_dic:
                dic = compress(path_split_list[1], path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv', crf, 0)
                size_cur = os.path.getsize(path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv') / float(1024 * 1024)
                tim = decompress(path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv', path_tmp)
                psnr_cur = psnr_class.tiff_psnr(path_split_list[1], path_tmp, 8)
                os.remove(path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv')
                record_dic[crf] = psnr_cur
            else:
                psnr_cur = record_dic[crf]
            #print("crf{crf}:{psnr}dB".format(crf=crf, psnr=psnr_cur))
            if psnr_cur > psnr_minimum:
                crf_end = crf
                crf_begin = crf + step
                if crf_begin > 51:
                    crf_begin = 51
                step = int(step / 2)
                dic_compress.append(dic)
                time_decompress.append(tim)
                size_mkv.append(size_cur)
                psnr.append(psnr_cur)
                break
    #delete the tmp folder
    shutil.rmtree(path_tmp)
    ret_list = [crf_end, dic_compress[-1], time_decompress[-1], size_mkv[-1], psnr[-1]]
    return ret_list

def find_bottom_crf(path_split_list, path_mkv, compress_ratio):
    """
    This function can find the bottom crf value that meets the compression ratio requirements.
    Args:
        path_split_list: the list whose components are the high8bits and low8bits tiff folder path
        path_mkv: a path that save the temp mkv file
        compress_ratio: the minimum compression ratio
    Return:It return the bottom crf value,the compression information and the mkv file size.
    """
    size_low8bits = get_folder_size(path_split_list[1])
    crf_begin = 51
    crf_end = 0
    step = 16
    record_dic = {}
    # this module can find the bottom crf value that meets the compression requirement
    # by decreasing the step size gradually
    while step > 0:
        for crf in range(crf_begin, crf_end - 1, -1 * step):
            if crf not in record_dic:
                compress(path_split_list[1], path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv', crf, 0)
                size_cur = os.path.getsize(path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv') / float(1024 * 1024)
                os.remove(path_mkv + '\\' + 'low_crf' + str(crf) + '.mkv')
                size_ratio = size_low8bits / size_cur
                record_dic[crf] = size_ratio
            else:
                size_ratio = record_dic[crf]
            #print("crf{crf} compress ratio:{ratio}  step:{step}".format(crf=crf, ratio=size_ratio, step=step))
            if size_ratio < compress_ratio:
                crf_end = crf
                crf_begin = crf + step
                if crf_begin > 51:
                    crf_begin = 51
                step = int(step / 2)
                break
    #get the compression and decompression information of the bottom crf value
    dic_compress = compress(path_split_list[1], path_mkv + '\\' + 'low_crf' + str(crf_begin) + '.mkv', crf_begin, 0)
    size_mkv = os.path.getsize(path_mkv + '\\' + 'low_crf' + str(crf_begin) + '.mkv') / float(1024 * 1024)
    makdir(path_mkv + '\\' + 'tmp')
    time_decompress = decompress(path_mkv + '\\' + 'low_crf' + str(crf_begin) + '.mkv', path_mkv + '\\' + 'tmp')
    psnr_class = PSNR.compute_psnr()
    psnr_ret = psnr_class.tiff_psnr(path_mkv + '\\' + 'tmp', path_split_list[1], 8)
    shutil.rmtree(path_mkv + '\\' + 'tmp')
    os.remove(path_mkv + '\\' + 'low_crf' + str(crf_begin) + '.mkv')
    ret_list = [crf_begin, dic_compress, time_decompress, size_mkv, psnr_ret]
    return ret_list

def makdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)

def get_folder_size(path):
    """
    Get the total size of all tiff files in a folder,and the size unit is MB.
    """
    total_size=0
    for file in glob.glob(path + '\\' + '*.tiff'):
        total_size = total_size + os.path.getsize(file)
    total_size = total_size / float(1024 * 1024)
    return round(total_size,3)

if __name__ == "__main__":
    #path_tiff = "D:\study\Ometiff\\0_0_tiff"
    #path_mkv = "D:\study\Ometiff\\test"
    #path_split_list = ["D:\study\Ometiff\\test\high8bits", "D:\study\Ometiff\\test\low8bits"]
    #path_decompress_tiff = "D:\study\Ometiff\\test\decompress"
    get_cmd_from_user()