#!/usr/bin/python3
#** encoding UTF-8 **#
from libtiff import TIFF
import glob
import os
import PSNR


def SetZero(PathTiffSource,PathTiffOut):
    """Set the lowest four bits of all the 16 bits tiff file in a folder to zero.

    Args:
        PathTiffSource:The path of the source tiff file folder.
        PathTiffOut:The path of the output tiff file folder.
    Return:This function has no returns.
    """

    dir=glob.glob(PathTiffSource+'\\'+'*.tiff')
    for SourceFile in dir:
        tif=TIFF.open(SourceFile,mode='r')
        img=tif.read_image()
        img=img-img%16  #lowest four bits set zero
        ImgName=os.path.basename(SourceFile).split('.')[0]
        OutFile=PathTiffOut+'\\'+'SetZero_'+ImgName+'.tiff'  #get the path of the output file
        TifPrecessed=TIFF.open(OutFile,'w')
        TifPrecessed.write_image(img)


# This module is used for debug
if __name__=='__main__':
    PathTiffSource="D:\study\Ometiff\\0_0"
    PathTIffOut="D:\study\Ometiff\\0_0_setzero"
    #SetZero(PathTiffSource,PathTIffOut)
    PSNRClass=PSNR.ComputePSNR()   #compute the PSNR between the source tiff file and the output tiff file
    PSNRClass.TiffPSNR(PathTiffSource,PathTIffOut)