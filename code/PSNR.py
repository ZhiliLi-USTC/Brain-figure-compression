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
        for i in range(self.StartNumber,self.EndNumber+1):
            ImgNotCompressedName=PathNotProcessed+'\\'+'slice_0_0_'+str(i)+'.jpg'
            ImgCompressedName=PathProcessed+'\\'+'0_0_'+str(i)+'.jpg'
            ImgNotCompressedArray=cv2.imread(ImgNotCompressedName,flags=0)
            ImgCompressedArray=cv2.imread(ImgCompressedName,flags=0)
            ArrayRowNum=ImgCompressedArray.shape[0]
            ArrayColNum=ImgCompressedArray.shape[1]
            diff=np.square(np.subtract(ImgCompressedArray,ImgNotCompressedArray)).sum()
            rmse=diff/ArrayRowNum/ArrayColNum
            Psnr=10*np.log10(255*255/rmse)
            PsnrTotal=PsnrTotal+Psnr
        PsnrAve=PsnrTotal/(self.EndNumber-self.StartNumber+1)
        print('PSNR:%f dB'%PsnrAve)
        return PsnrAve


    def TiffPSNR(self,PathSource,PathSetZero):
        """Compute average PSNR of the 16 bits tiff files in the two folders.

        Args:
            PathSource: The path of one tiff file folder which includes 16 bits tiff files.
            PathCompressed: The path of another tiff file folder which includes 16 bits tiff files.

        Returns:
            It returns the average PSNR which data type is float.
        """
        PsnrTotal=0
        for i in range(self.StartNumber,self.EndNumber+1):
            FileSource=PathSource+'\\'+'slice_0_0_'+str(i)+'.tiff'
            FileSetZero=PathSetZero+'\\'+'SetZero_'+'slice_0_0_'+str(i)+'.tiff'
            TiffSource=TIFF.open(FileSource,'r')
            TiffSetZero=TIFF.open(FileSetZero,'r')
            ArraySource=TiffSource.read_image()
            ArraySetZero=TiffSetZero.read_image()
            ArrayRawNum=ArraySource.shape[0]
            ArrayColNum=ArraySource.shape[1]
            diff=np.square(np.subtract(ArraySetZero,ArraySource)).sum()
            rmse=diff/ArrayRawNum/ArrayColNum
            Psnr=20*np.log10(65535/np.sqrt(rmse))
            PsnrTotal=PsnrTotal+Psnr
        PsnrAve=PsnrTotal/(self.EndNumber-self.StartNumber+1)
        print('PSNR:%f dB'%PsnrAve)
        return PsnrAve


#for debug
if __name__=="__main__":
    PathNOtCompressed="D:\study\Ometiff\\0_0_jpg"
    PathCompressed="D:\study\Ometiff\\0_0_jpg_decompress"
    psnr=ComputePSNR()
    psnr.JpgPSNR(PathNOtCompressed,PathCompressed)