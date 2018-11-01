#!/usr/bin/python3
#** encoding UTF-8 **#
import os
import time
import subprocess
import glob
from libtiff import TIFF
from scipy import misc


def ExtractToJpg(path_exe,path_source,path_out_tiff):
    """
    This function extract tiff file from Raw.ome.tiff,and then convert the tiff file to jpg file.

    Args:
        path_exe: the path of the external executable file Ometiff.exe which can extract one simple tiff file from Raw.ome.tif.
        path_source:the path of the complicate tiff file Raw.ome.tif
        path_out_tiff:the path you want to save the output simple tiff file
    Returns: No returns.
    """

    index=[30,849,0,784,49,850]  #this is the range of T(the third parameter in C,Z,T of Raw.ome.tiff) which can be extracted
    for c in range(1):
        for z in range(1):
            for t in range(index[2*z],index[2*z+1]):
                path_out=path_out_tiff+'\\'+str(c)+'_'+str(z)
                makdir(path_out)
                filename='slice_'+str(c)+'_'+str(z)+'_'+str(t)+'.tiff'
                com=path_exe+' -s '+path_source+ ' -o '+path_out+'\\'+filename+' -d '+str(c)+','+str(z)+','+str(t)
                ret=subprocess.Popen(com,stdout=subprocess.PIPE)  #call the external exe
        time.sleep(0.5)    #sleep 0.5s make sure that all the tiff file in one Z can be extracted successfully
        path_out_jpg=path_out+'_jpg'
        makdir(path_out_jpg)
        dir=glob.glob(path_out+'\\'+'*.tiff')
        for file in dir:
            print(file)
            tiff_to_jpg(file,path_out_jpg)


def makdir(path):
    folder=os.path.exists(path)
    if not folder:
        os.makedirs(path)


def tiff_to_jpg(tiff_filename,path_out_jpg):
    """
    This function is designed to convert the tiff file to jpg file.

    Args:
        tiff_filename:the path of tiff file.
        path_out_jpg:the path of output jpg file folder.
    Returns:No returns.
    """
    tif=TIFF.open(tiff_filename,mode='r')
    img=tif.read_image()
    file_name=os.path.basename(tiff_filename)
    path=path_out_jpg+'\\'+str.split(file_name,'.')[0]+'.jpg'
    misc.imsave(path,img)


#for debug
if __name__ == '__main__':
    path_exe = "D:\study\Ometiff\Ometiff.exe"
    path_source = "D:\study\Ometiff\Raw.ome.tif"
    path_out_tiff = "D:\study\Ometiff"
    ExtractToJpg(path_exe,path_source,path_out_tiff)