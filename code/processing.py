#!/usr/bin/python3
#** encoding UTF-8 **#
import os
import glob
import numpy as np
from libtiff import TIFF
import subprocess


def ExtractToSingleFile(PathExe,PathSource,PathOut,FileType):
    """
    This function extracts jpg file from Raw.ome.tiff,and then convert the tiff file to jpg file.

    Args:
        PathExe: the path of the external executable file Ometiff.exe which can extract one simple file from Raw.ome.tif
        PathSource:the path of the complicate tiff file Raw.ome.tif
        PathOut:the path you want to save the output file
        FileType:the specific file type you want to extract,such as tiff ,jpg and etc
    Returns: No returns.
    """

    index=[30,849,0,784,49,850]  #this is the range of T(the third parameter in C,Z,T of Raw.ome.tiff) which can be extracted
    for c in range(1):
        for z in range(1):
            for t in range(index[2*z],index[2*z+1]):
                path_out=PathOut+'\\'+str(c)+'_'+str(z)+'_'+FileType
                makdir(path_out)
                filename=str(c)+'_'+str(z)+'_'+str(t)+'.'+FileType
                com=PathExe+' -s '+PathSource+ ' -o '+path_out+'\\'+filename+' -d '+str(c)+','+str(z)+','+str(t)
                ret=subprocess.Popen(com,stdout=subprocess.PIPE)  #call the external exe


def TiffLowFourBitsSetZero(PathTiffSource,PathTiffOut):
    """Set the lowest four bits of all the 16 bits tiff file in a folder to zero.

    Args:
        PathTiffSource:the path of the source tiff file folder
        PathTiffOut:the path of the output tiff file folder
    Return:This function has no returns.
    """

    dir=glob.glob(PathTiffSource+'\\'+'*.tiff')
    for SourceFile in dir:
        tif=TIFF.open(SourceFile,mode='r')
        img=tif.read_image()
        img=img-img%16  #lowest four bits set zero
        ImgName=os.path.basename(SourceFile)
        OutFile=PathTiffOut+'\\'+ImgName  #get the path of the output file
        TifProcessed=TIFF.open(OutFile,'w')
        TifProcessed.write_image(img)


def TiffSplit(PathTiffSource,PathTiffOut):
    """
    This function splits one 16bits tiff file to two different 8bits tiff files.
    The strategy of split is setting the lowest 8 bits of the source 16 bits file as the pixel value of one split file and the same as the highest 8 bits.

    Args:
        PathTiffSource:the path of the source tiff file folder
        PathTiffOut:the path of the output tiff file folder

    Returns:No returns
    """
    PathOutLow=PathTiffOut+'\\'+'low8bits'
    PathOutHig=PathTiffOut+'\\'+'high8bits'
    makdir(PathOutLow)
    makdir(PathOutHig)
    for file in glob.glob(PathTiffSource+'\\'+'*.tiff'):
        tif=TIFF.open(file,'r')
        Img=tif.read_image()
        ImgLow8Bits=Img%256
        ImgHig8Bits=Img/256
        ImgLow8Bits=ImgLow8Bits.astype(np.uint8)
        ImgHig8Bits=ImgHig8Bits.astype(np.uint8)
        ImgName=os.path.basename(file)
        TifSplitLow=TIFF.open(PathOutLow+'\\'+ImgName,'w')
        TifSplitLow.write_image(ImgLow8Bits)
        TifSplitHig=TIFF.open(PathOutHig+'\\'+ImgName,'w')
        TifSplitHig.write_image(ImgHig8Bits)


def TiffMerge(PathTiffHigh,PathTiffLow,PathMerge,StartNum,EndNum):
    """
    Args:
    PathTiffHigh:the path of 8bits tiff file formed by the highest 8 bits of the origin 16its tiff file
    PathTiffLow:the path of 8bits tiff file formed by the lowest 8 bits of the origin 16its tiff file
    PathMerge:the path of the output merged 16bits tiff file
    StartNum:the index where you want to begin to merge
    EndNum:the index where you want to end to merge

    Return:no returns
    """

    for i in range(StartNum,EndNum+1):
        FileHigh=TIFF.open(PathTiffHigh+'\\'+'0_0_'+str(i)+'.tiff','r')
        FileLow=TIFF.open(PathTiffLow+'\\'+'0_0_'+str(i)+'.tiff','r')
        ImgHigh=FileHigh.read_image().astype(np.uint16)
        ImgLow=FileLow.read_image().astype(np.uint16)
        ImgMerge=ImgHigh*256+ImgLow
        FileMerge=TIFF.open(PathMerge+'\\'+'0_0_'+str(i)+'.tiff','w')
        FileMerge.write_image(ImgMerge)


def makdir(path):
    folder=os.path.exists(path)
    if not folder:
        os.makedirs(path)


#for debug
if __name__ == '__main__':
    path_exe = "D:\study\Ometiff\Ometiff.exe"
    path_source = "D:\study\Ometiff\Raw.ome.tif"
    path_out = "D:\study\Ometiff"
    path_tiff="D:\study\Ometiff\\0_0_tiff"
    path_split="D:\study\Ometiff\\0_0_tiff_split"
    path_zero="D:\study\Ometiff\\0_0_setzero"
    #ExtractToSingleFile(path_exe,path_source,path_out,'jpg')
    #ExtractToSingleFile(path_exe, path_source, path_out, 'tiff')
    #TiffSplit(path_tiff,path_split)
    #TiffLowFourBitsSetZero(path_tiff,path_zero)
    TiffMerge(path_split+'\\'+'high8bits',path_split+'\\'+'low_decompress',path_split+'\\'+'merge_new',30,848)