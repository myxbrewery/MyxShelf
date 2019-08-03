import imutils
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import cv2

import time


def get_all_barcodes(img_dir):
    # load the input image
    image = cv2.imread(img_dir)
    # find the barcodes in the image and decode each of the barcodes
    barcodes = pyzbar.decode(image)
    return barcodes, image

def parse_barcodes(barcodes, image):
    res = []
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw the
        # bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
 
    # the barcode data is a bytes object so if we want to draw it on
    # our output image we need to convert it to a string first
    barcodeData = barcode.data.decode("utf-8")
    barcodeType = barcode.type
 
    # draw the barcode data and barcode type on the image
    text = "{} ({})".format(barcodeData, barcodeType)
    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.5, (0, 0, 255), 2)
 
    # print the barcode type and data to the terminal
    print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
    res.append(barcodeData)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    return res


def cam_output(buffer):
    """
    Starts a video stream and outputs QR, if any, to the buffer
    """
    vs = VideoSteam(usePiCamera=True).start()
    time.sleep(2)
    while True:
        pass



if __name__ == "__main__":
     # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image",
                    help="path to input image")
    ap.add_argument("-c", "--camera", type=bool, default=False, help="use camera?")
    args = vars(ap.parse_args()) 
    img_dir = args["image"]
    camera_mode = args["camera"]
    if camera_mode:
        vs = VideoStream(usePiCamera=True).start()
        time.sleep(2)
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            barcodes = pyzbar.decode(frame)
            print([barcode.data for barcode in barcodes])
    else:
        barcodes, image = get_all_barcodes(img_dir)
        vs = VideoStream(usePiCamera=True).start()
        print(parse_barcodes(barcodes, image))
