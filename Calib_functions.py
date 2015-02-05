#Calib_function.py
#Created by Chris Rillahan
#Last Updated: 08/26/2014
#Written with Python 2.7.2, OpenCV 2.4.8 and NumPy 1.8.0

#This file contains two functions.  ImageCollect is responsible for collected a series of
#calibration images from a standard calibration checkerboard pattern.  ImageProcessing
#takes those calibration images and calculates the intrinsic matrix and distortion
#coefficents for the camera.  These functions are typically called from Cam_calib.py.

import numpy as np
import cv2

#The ImageCollect function requires two input parameters.  Filename is the name of the file
#in which checkerboard images will be collected from.  n_boards is the number of images of
#the checkerboard which are needed.  In the current writing of the functio, an additional 5
#images will be taken.  This ensures that the processing step has the correct number of images
#and can skip an image if the program has issues.

#This function loads the video file into a data space called video.  It then collects various
#meta-data about the file for later inputs.  The function then enters a loop in which it loops
#through each image, displays the image and waits for a fixed amount of time before displaying
#the next image.  The playback speed can be adjusted in the waitKey command.  During the loop
#checkerboard images can be collected by pressing the spacebar.  Each image will be saved as a
#*.png into the directory which stores this file.  The ESC key will terminate the function.
#The function will end once the correct number of images are collected or the video ends.
#For the processing step, try to collect all the images before the video ends.

def ImageCollect(filename, n_boards):
    #Collect Calibration Images
    print('-----------------------------------------------------------------')
    print('Loading video...')

    #Load the file given to the function
    video = cv2.VideoCapture(filename)

    #Collect metadata about the file.
    FPS = video.get(cv2.cv.CV_CAP_PROP_FPS)
    FrameDuration = 1/(FPS/1000)
    width = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    size = (int(width), int(height))
    total_frames = video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

    #Initializes the frame counter and collected_image counter
    current_frame = 0
    collected_images = 0

    #Video loop.  Press spacebar to collect images.  ESC terminates the function.
    while current_frame < total_frames:
        success, image = video.read()
        current_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        cv2.imshow('Video', image)
        k = cv2.waitKey(int(FrameDuration)*2)
        if collected_images == n_boards+5: 
            break
        if k == 32:
            collected_images += 1
            cv2.imwrite('Calibration_Image' + str(collected_images) + '.png', image)
            print(str(collected_images) + ' images collected.')
        if k == 27:
            break
    
    #Clean up
    video.release()
    cv2.destroyAllWindows()


#The ImageProcessing function performs the calibration of the camera based on the images
#collected during ImageCollect function.  This function will look for the images in the folder
#which contains this file.  The function inputs are the number of boards which will be used for
#calibration (n_boards), the number of squares on the checkerboard (board_w, board_h) as
#determined by the inside points (i.e. where the black squares touch).  board_dim is the actual
#size of the square, this should be an integer.  It is assumed that the checkerboard square are
#square.

#This function first initializes a series of variables. Opts will store the true object points
#(i.e. checkerboard points).  Ipts will store the points as determined by the calibration images.
#The function then loops through each image.  Each image is converted to grayscale, and the
#checkerboard corners are located.  If it is successful at finding the correct number of corners
#then the true points and the measured points are stored into opts and ipts, respectively. The
#image with the checkerboard points are then displays.  If the points are not found that image
#is skipped.  Once the desired number of checkerboard points are acquired the calibration
#parameters (intrinsic matrix and distortion coefficients) are calculated.

#The distortion parameter are saved into a numpy file (calibration_data.npz).  The total
#total reprojection error is calculated by comparing the "true" checkerboard points to the
#image measured points once the image is undistorted.  The total reprojection error should be
#close to zero.

#Finally the function will go through the calbration images and display the undistorted image.
    
def ImageProcessing(n_boards, board_w, board_h, board_dim):
    #Initializing variables
    board_n = board_w * board_h
    opts = []
    ipts = []
    npts = np.zeros((n_boards, 1), np.int32)
    intrinsic_matrix = np.zeros((3, 3), np.float32)
    distCoeffs = np.zeros((5, 1), np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    # prepare object points based on the actual dimensions of the calibration board
    # like (0,0,0), (25,0,0), (50,0,0) ....,(200,125,0)
    objp = np.zeros((board_h*board_w,3), np.float32)
    objp[:,:2] = np.mgrid[0:(board_w*board_dim):board_dim,0:(board_h*board_dim):board_dim].T.reshape(-1,2)

    #Loop through the images.  Find checkerboard corners and save the data to ipts.
    for i in range(1, n_boards + 1):
    
        #Loading images
        print 'Loading... Calibration_Image' + str(i) + '.png' 
        image = cv2.imread('Calibration_Image' + str(i) + '.png')
    
        #Converting to grayscale
        grey_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        #Find chessboard corners
        found, corners = cv2.findChessboardCorners(grey_image, (board_w,board_h),cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH + cv2.cv.CV_CALIB_CB_NORMALIZE_IMAGE)

        if found == True:

            #Add the "true" checkerboard corners
            opts.append(objp)

            #Improve the accuracy of the checkerboard corners found in the image and save them to the ipts variable.
            cv2.cornerSubPix(grey_image, corners, (20, 20), (-1, -1), criteria)
            ipts.append(corners)

            #Draw chessboard corners
            cv2.drawChessboardCorners(image, (board_w, board_h), corners, found)
        
            #Show the image with the chessboard corners overlaid.
            cv2.imshow("Corners", image)

        char = cv2.waitKey(0)

    cv2.destroyWindow("Corners") 
    
    print ''
    print 'Finished processes images.'

    #Calibrate the camera
    print 'Running Calibrations...'
    print(' ')
    ret, intrinsic_matrix, distCoeff, rvecs, tvecs = cv2.calibrateCamera(opts, ipts, grey_image.shape[::-1],None,None)

    #Save matrices
    print('Intrinsic Matrix: ')
    print(str(intrinsic_matrix))
    print(' ')
    print('DistCoeff Right Camera: ')
    print(str(distCoeff))
    print(' ') 

    #Save data
    print 'Saving data file...'
    np.savez('calibration_data', distCoeff=distCoeff, intrinsic_matrix=intrinsic_matrix)
    print 'Calibration complete'

    #Calculate the total reprojection error.  The closer to zero the better.
    tot_error = 0
    for i in xrange(len(opts)):
        imgpoints2, _ = cv2.projectPoints(opts[i], rvecs[i], tvecs[i], intrinsic_matrix, distCoeff)
        error = cv2.norm(ipts[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        tot_error += error

    print "total reprojection error: ", tot_error/len(opts)

    #Undistort Images
    for i in range(1, n_boards + 1):
    
        #Loading images
        print 'Loading... Calibration_Image' + str(i) + '.png' 
        image = cv2.imread('Calibration_Image' + str(i) + '.png')

        # undistort
        dst = cv2.undistort(image, intrinsic_matrix, distCoeff, None)

        cv2.imshow('Undisorted Image',dst)

        char = cv2.waitKey(0)

    cv2.destroyAllWindows()

    
