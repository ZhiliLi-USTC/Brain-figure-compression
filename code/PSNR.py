#!/usr/bin/python3
#** encoding UTF-8 **#
import numpy as np
import cv2
from libtiff import TIFF


class ComputePSNR:
    """Summary of class here.

    There are two functions used to compute Peak Signal Noise Ratio(PSNR) in the class.
    One can compute the average PSNR of 8 bits jpg files in two folders.
    The other is designed to compute the average PSNR of 16 bits tiff files in two folders.

    More details are in the function annotations.
    """

    def __init__(self):
        self.StartNumber=30
        self.EndNumber=848


    def JpgPSNR(self,PathNotProcessed,PathProcessed):
        """Compute average PSNR of the 8 bits jpg files in the two folders.

        Args:
            PathNotCompressed: The path of jpg file folder which includes 8 bits jpg files without being processed by ffmpeg.
            PathCompressed: The path of jpg file folder which includes 8 bits jpg files with being compressed and decompressed by ffmpeg.

        Returns:
            It returns the average PSNR which data type is float.
        """
        PsnrTotal=0
        MaxVal=2**8-1  #the max value in a 8 bits picture
        for i in range(self.StartNumber,self.EndNumber+1):
            ImgNotCompressedName=PathNotProcessed+'\\'+'0_0_'+str(i)+'.jpg'
            ImgCompressedName=PathProcessed+'\\'+'0_0_'+str(i)+'.jpg'
            ImgNotCompressedArray=cv2.imread(ImgNotCompressedName,flags=0).astype(np.int64)
            ImgCompressedArray=cv2.imread(ImgCompressedName,flags=0).astype(np.int64)
            ArrayRowNum=ImgCompressedArray.shape[0]
            ArrayColNum=ImgCompressedArray.shape[1]
            #diff=np.square(ImgCompressedArray-ImgNotCompressedArray)
            diff=np.square(cv2.absdiff(ImgCompressedArray,ImgNotCompressedArray))
            diff_sum=diff.sum()
            MSE=diff_sum/ArrayRowNum/ArrayColNum
            Psnr=10*np.log10(MaxVal*MaxVal/MSE)
            PsnrTotal=PsnrTotal+Psnr
        PsnrAve=PsnrTotal/(self.EndNumber-self.StartNumber+1)
        print('PSNR:%f dB'%PsnrAve)
        return PsnrAve


    def TiffPSNR(self,PathFirst,PathSecond,Bitnum):
        """Compute average PSNR of the specific bit tiff files in the two folders.

        Args:
            PathFirst: The path of one tiff file folder which includes specific bit tiff files.
            PathSecond: The path of another tiff file folder which includes specific bit tiff files.
            Bitnum:the bit number of the input tiff file.

        Returns:
            It returns the average PSNR which data type is float.
        """
        PsnrTotal=0
        MaxVal=2**Bitnum-1
        count=0
        for i in range(self.StartNumber,self.EndNumber+1):
            FileFirst=PathFirst+'\\'+'0_0_'+str(i)+'.tiff'
            FileSecond=PathSecond+'\\'+'0_0_'+str(i)+'.tiff'
            TiffFirst=TIFF.open(FileFirst,'r')
            TiffSecond=TIFF.open(FileSecond,'r')
            ArrayFirst=TiffFirst.read_image().astype(np.int64)
            ArraySecond=TiffSecond.read_image().astype(np.int64)
            #ArrayFirst = TiffFirst.read_image()
            #ArraySecond = TiffSecond.read_image()
            ArrayRawNum=ArrayFirst.shape[0]
            ArrayColNum=ArrayFirst.shape[1]
            diff=np.square(cv2.absdiff(ArrayFirst,ArraySecond))
            #diff=np.square(ArraySecond-ArrayFirst)
            diff_sum=diff.sum()
            if diff_sum != 0:
                MSE=diff_sum/ArrayRawNum/ArrayColNum
                Psnr=10*np.log10(MaxVal*MaxVal/MSE)
                PsnrTotal=PsnrTotal+Psnr
                count=count+1
        PsnrAve=PsnrTotal/(count)
        print('{count} tiff average PSNR:{psnr} dB'.format(count=count,psnr=PsnrAve))
        return PsnrAve


#for debug
if __name__=="__main__":
    PathHighDe="D:\study\Ometiff\\0_0_tiff_split\high_decompress"
    PathHigh="D:\study\Ometiff\\0_0_tiff_split\high8bits"
    PathLowDe = "D:\study\Ometiff\\0_0_tiff_split\low_decompress"
    PathLow = "D:\study\Ometiff\\0_0_tiff_split\low8bits"
    psnr=ComputePSNR()
    #print('high')
    #psnr.TiffPSNR(PathHigh,PathHighDe,8)
    #print('low:')
    #psnr.TiffPSNR(PathLow,PathLowDe,8)
    psnr.TiffPSNR("D:\study\Ometiff\\0_0_tiff","D:\study\Ometiff\\0_0_tiff_split\merge_new",16)
