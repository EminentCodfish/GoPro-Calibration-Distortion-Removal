#Undisort.py
#Created by Chris Rillahan
#Last Updated: 02/04/2015
#Written with Python 2.7.2, OpenCV 2.4.8 and NumPy 1.8.0

#This program takes a video file and removes the camera distortion based on the
#camera calibration parameters.  The filename and the calibration data filenames
#should be changed where appropriate.  Currently, the program is set to search for
#these files in the folder in which this file is located.

#This program first loads the calibration data.  Secondly, the video is loaded and
#the metadata is derived from the file.  The export parameters and file structure
#are then set-up.  The file then loops through each frame from the input video,
#undistorts the frame and then saves the resulting frame into the output video.
#It should be noted that the audio from the input file is not transfered to the
#output file.

import numpy as np
import cv2, time, sys

filename = 'GOPR0028.MP4'

print 'Loading data files'

npz_calib_file = np.load('calibration_data.npz')

distCoeff = npz_calib_file['distCoeff']
intrinsic_matrix = npz_calib_file['intrinsic_matrix']

npz_calib_file.close()

print('Finished loading files')
print(' ')
print('Starting to undistort the video....')

#Opens the video import and sets parameters
video = cv2.VideoCapture(filename)
#Checks to see if a the video was properly imported
status = video.isOpened()

if status == True:
    FPS = video.get(cv2.cv.CV_CAP_PROP_FPS)
    width = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    size = (int(width), int(height))
    total_frames = video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    frame_lapse = (1/FPS)*1000

    #Initializes the export video file
    codec = cv2.cv.CV_FOURCC('D','I','V','X')
    video_out = cv2.VideoWriter(str(filename[:-4])+'_undistored.avi', codec, FPS, size, 1)

    #Initializes the frame counter
    current_frame = 0
    start = time.clock()

    while current_frame < total_frames:
        success, image = video.read()
        current_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)

        dst = cv2.undistort(image, intrinsic_matrix, distCoeff, None)
    
        video_out.write(dst)
    
    video.release()
    video_out.release()
    duration = (time.clock()-float(start))/60

    print(' ')
    print('Finished undistorting the video')
    print('This video took:' + str(duration) + ' minutes')
else:
    print("Error: Video failed to load")
    sys.exit()


