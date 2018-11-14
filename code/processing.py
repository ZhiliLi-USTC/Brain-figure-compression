#!/usr/bin/python3
#** encoding UTF-8 **#
import os
import glob
import numpy as np
from libtiff import TIFF
import subprocess
import PSNR


def extract_to_single_file(path_exe, path_source, path_file_out, file_type):
    """
    This function extracts jpg file from Raw.ome.tiff,and then convert the tiff file to jpg file.

    Args:
        path_exe: the path of the external executable file Ometiff.exe which can extract one simple file from Raw.ome.tif
        path_source:the path of the complicate tiff file Raw.ome.tif
        path_file_out:the path you want to save the output file
        file_type:the specific file type you want to extract,such as tiff ,jpg and etc
    Returns: No returns.
    """

    index = [30, 849, 0, 784, 49, 850]  #this is the range of T(the third parameter in C,Z,T of Raw.ome.tiff) which can be extracted
    for c in range(1):
        for z in range(1):
            for t in range(index[2 * z], index[2 * z + 1]):
                path_out = path_file_out + '\\' + str(c) + '_' + str(z) + '_' + file_type
                makdir(path_out)
                filename = str(c) + '_' + str(z) + '_' + str(t) + '.' + file_type
                com = path_exe + ' -s ' + path_source + ' -o ' + path_out + '\\'\
                      + filename + ' -d ' + str(c) + ',' + str(z) + ',' + str(t)
                subprocess.Popen(com, stdout=subprocess.PIPE)  #call the external exe


def tiff_low_four_bits_set_zero(path_tiff_source, path_tiff_out):
    """Set the lowest four bits of all the 16 bits tiff file in a folder to zero.

    Args:
        path_tiff_source:the path of the source tiff file folder
        path_tiff_out:the path of the output tiff file folder
    Return:This function has no returns.
    """

    dir = glob.glob(path_tiff_source + '\\' + '*.tiff')
    for source_file in dir:
        tif = TIFF.open(source_file, mode='r')
        img = tif.read_image()
        img = img - img % 16  #lowest four bits set zero
        img_name = os.path.basename(source_file)
        out_file = path_tiff_out + '\\' + img_name  #get the path of the output file
        tif_processed = TIFF.open(out_file, 'w')
        tif_processed.write_image(img)


def tiff_split(path_tiff_source, path_tiff_out):
    """
    This function splits one 16bits tiff file to two different 8bits tiff files.
    The strategy of split is setting the lowest 8 bits of the source 16 bits file as the pixel
    value of one split file and the same as the highest 8 bits.

    Args:
        path_tiff_source:the path of the source tiff file folder
        path_tiff_out:the path of the output tiff file folder

    Returns:return a list,the first element of the list is the path of the output high 8 tiff bits file
    and the second element of the list is the path of the output low 8 bits tiff file
    """
    path_out_low = path_tiff_out + '\\' + 'low8bits'
    path_out_hig = path_tiff_out + '\\' + 'high8bits'
    path_out_list=[path_out_hig,path_out_low]
    makdir(path_out_low)
    makdir(path_out_hig)
    for file in glob.glob(path_tiff_source + '\\' + '*.tiff'):
        tif = TIFF.open(file, 'r')
        img = tif.read_image()
        img_low_8bits = img % 256
        img_hig_8bits = img / 256
        img_low_8bits = img_low_8bits.astype(np.uint8)
        img_hig_8bits = img_hig_8bits.astype(np.uint8)
        img_name = os.path.basename(file)
        tif_split_low = TIFF.open(path_out_low + '\\' + img_name, 'w')
        tif_split_low.write_image(img_low_8bits)
        tif_split_hig = TIFF.open(path_out_hig + '\\' + img_name, 'w')
        tif_split_hig.write_image(img_hig_8bits)
    return path_out_list


def tiff_merge(path_tiff_high, path_tiff_low, path_merge, start_num, end_num):
    """
    Args:
    path_tiff_high:the path of 8bits tiff file formed by the highest 8 bits of the origin 16its tiff file
    path_tiff_low:the path of 8bits tiff file formed by the lowest 8 bits of the origin 16its tiff file
    path_merge:the path of the output merged 16bits tiff file
    start_num:the index where you want to begin to merge
    end_num:the index where you want to end to merge

    Return:no returns
    """

    for i in range(start_num, end_num + 1):
        file_high = TIFF.open(path_tiff_high + '\\' + '0_0_' + str(i) + '.tiff', 'r')
        file_low = TIFF.open(path_tiff_low + '\\' + '0_0_' + str(i) + '.tiff', 'r')
        img_high = file_high.read_image().astype(np.uint16)
        img_low = file_low.read_image().astype(np.uint16)
        img_merge = img_high * 256 + img_low
        file_merge = TIFF.open(path_merge + '\\' + '0_0_' + str(i) + '.tiff', 'w')
        file_merge.write_image(img_merge)


def makdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


#for debug
if __name__ == '__main__':
    path_exe = "D:\study\Ometiff\Ometiff.exe"
    path_source = "D:\study\Ometiff\Raw.ome.tif"
    path_out = "D:\study\Ometiff"
    path_tiff = "D:\study\Ometiff\\0_0_tiff"
    path_split = "D:\study\Ometiff\\0_0_tiff_split"
    path_zero = "D:\study\Ometiff\\0_0_setzero"
    extract_to_single_file(path_exe,path_source,path_out,'jpg')
    #etract_to_single_file(path_exe, path_source, path_out, 'tiff')
    #tiff_split(path_tiff,path_split)
    #tiff_low_four_bits_set_zero(path_tiff,path_zero)
    #tiff_merge(path_split+'\\'+'high_lossless',path_split+'\\'+'low_decompress',path_split+'\\'+'test',583,583)

    #tiff_merge(path_split + '\\' + 'high_lossless', path_split + '\\' + 'low_crf16',\
    # path_split + '\\' + 'merge_16', 30, 848)
    #os.system('sleep 0.5')
    #psnrclass=PSNR.compute_PSNR()
    #psnrclass.tiff_PSNR("D:\study\Ometiff\\0_0_tiff","D:\study\Ometiff\\0_0_tiff_split\\merge_16",16)
