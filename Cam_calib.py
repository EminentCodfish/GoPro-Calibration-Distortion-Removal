#Cam_calib.py
#Created by Chris Rillahan
#Last Updated: 08/26/2014
#Written with Python 2.7.2, OpenCV 2.4.8 and NumPy 1.8.0

#This program functions to calculate the distortion parameters of a GoPro camera.
#A video must first be taken with a GoPro of a chessboard pattern in a moved to a
#variety of positions in the field of view.  This program relies on the functions
#writting in Calib_functions.py.  This function essential sets the imput variable
#and then call the two functions (ImageCollect and ImageProcessing) from Calib_functions.py.

import Calib_functions as cf

#Import Information
filename = 'GOPR0005.MP4'
#Input the number of board images
n_boards = 20
#Input the number of squares on the board (width and height)
board_w = 9
board_h = 6
#Board dimensions (typically in cm)
board_dim = 25
#Image resolution
image_size = (1920, 1080)

print("Starting camera calibration....")
print("Step 1: Image Collection")
print("We will playback the calibration video.  Press the spacebar to save")
print("calibration images.")
print(" ")
print('We will collect ' + str(n_boards) + ' calibration images.')

cf.ImageCollect(filename, n_boards+5)

print(' ')
print('All the calibration images are collected.')
print('------------------------------------------------------------------------')
print('Step 2: Calibration')
print('We will analyze the images take and calibrate the camera.')
print('Press the esc button to close the image windows as they appear.')
print(' ')

cf.ImageProcessing(n_boards, board_w, board_h, board_dim)
