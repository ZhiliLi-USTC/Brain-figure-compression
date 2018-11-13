#!/usr/bin/python3
#** encoding UTF-8 **#
import numpy as np
import cv2
from libtiff import TIFF


class compute_psnr():
    """Summary of class here.

    There are two functions used to compute Peak Signal Noise Ratio(PSNR) in the class.
    One can compute the average PSNR of 8 bits jpg files in two folders.
    The other is designed to compute the average PSNR of 16 bits tiff files in two folders.

    More details are in the function annotations.
    """

    def __init__(self):
        self.start_number = 30
        self.end_number = 848


    def jpg_psnr(self, path_not_processed, path_processed):
        """Compute average PSNR of the 8 bits jpg files in the two folders.
        Args:
            path_not_compressed: The path of jpg file folder which includes 8 bits jpg files without being processed by ffmpeg.
            path_compressed: The path of jpg file folder which includes 8 bits jpg files with being compressed and decompressed by ffmpeg.

        Returns:
            It returns the average PSNR which data type is float.
        """
        psnr_total = 0
        max_val = 2**8 - 1  #the max value in a 8 bits picture
        for i in range(self.start_number, self.end_number+1):
            img_not_compressed_name = path_not_processed + '\\' + '0_0_' + str(i) + '.jpg'
            img_compressed_name = path_processed + '\\' + '0_0_' + str(i) + '.jpg'
            img_not_compressed_array = cv2.imread(img_not_compressed_name, flags=0).astype(np.int64)
            img_compressed_array = cv2.imread(img_compressed_name, flags=0).astype(np.int64)
            array_row_num = img_compressed_array.shape[0]
            array_col_num = img_compressed_array.shape[1]
            #diff=np.square(ImgCompressedArray-ImgNotCompressedArray)
            diff = np.square(cv2.absdiff(img_compressed_array, img_not_compressed_array))
            diff_sum = diff.sum()
            mse = diff_sum / array_row_num / array_col_num
            Psnr = 10 * np.log10(max_val * max_val / mse)
            psnr_total = psnr_total + Psnr
        psnr_ave = psnr_total / (self.end_number - self.start_number + 1)
        #print('PSNR:%f dB'%psnr_ave)
        return psnr_ave


    def tiff_psnr(self, path_first, path_second, bit_num):
        """Compute average PSNR of the specific bit tiff files in the two folders.

        Args:
            path_first: The path of one tiff file folder which includes specific bit tiff files.
            path_second: The path of another tiff file folder which includes specific bit tiff files.
            bit_num:the bit number of the input tiff file.

        Returns:
            If the return is a positive float number,it means the average PSNR of the files in the two different folders.
            If the return is -1,it means all the files are exactly the same and the psnr is infinite.
        """
        psnr_total = 0
        max_val = 2 ** bit_num - 1
        count = 0
        for i in range(self.start_number, self.end_number + 1):
            file_first = path_first + '\\' + '0_0_' + str(i) + '.tiff'
            file_second = path_second + '\\' + '0_0_' + str(i) + '.tiff'
            tiff_first = TIFF.open(file_first, 'r')
            tiff_second = TIFF.open(file_second, 'r')
            array_first = tiff_first.read_image().astype(np.int64)
            array_second = tiff_second.read_image().astype(np.int64)
            #ArrayFirst = TiffFirst.read_image()
            #ArraySecond = TiffSecond.read_image()
            array_raw_num = array_first.shape[0]
            array_col_num = array_first.shape[1]
            diff = np.square(cv2.absdiff(array_first, array_second))
            #diff=np.square(ArraySecond-ArrayFirst)
            diff_sum = diff.sum()
            if diff_sum != 0:
                mse = diff_sum / array_raw_num / array_col_num
                psnr = 10 * np.log10(max_val * max_val / mse)
                psnr_total = psnr_total + psnr
                count = count + 1
        if count == 0:
            print('The files in the two different folders are exactly the same!')
            return -1
        psnr_ave = psnr_total / (count)
        #print('{count} tiff average PSNR:{psnr} dB'.format(count=count, psnr=psnr_ave))
        return psnr_ave


#for debug
if __name__ == "__main__":
    PathHighDe = "D:\study\Ometiff\\0_0_tiff_split\high_decompress"
    PathHigh = "D:\study\Ometiff\\0_0_tiff_split\high8bits"
    PathLowDe = "D:\study\Ometiff\\0_0_tiff_split\low_decompress"
    PathLow = "D:\study\Ometiff\\0_0_tiff_split\low8bits"
    PathHighLossless = "D:\study\Ometiff\\0_0_tiff_split\high_lossless"
    PathLowCrf = "D:\study\Ometiff\\0_0_tiff_split\low_crf20"
    psnr = compute_psnr()
    #print('high')
    #psnr.tiff_PSNR(PathHigh,PathHighLossless,8)
    print('low:')
    psnr.tiff_psnr(PathLow, PathLowCrf, 8)
    #psnr.tiff_PSNR("D:\study\Ometiff\\0_0_tiff","D:\study\Ometiff\\0_0_tiff_split\merge_16",16)
