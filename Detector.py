import cv2 as cv
import uuid
import os
import time
import tensorflow as tf
import numpy as np
from tensorflow.python.keras.utils.data_utils import get_file

np.random.seed(20)


class Detector:
    def __init__(self):
        pass

    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()

        # Colors list:
        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))

        #print(len(self.classesList), len(self.colorList))

    def downloadModel(self, modelURL):
        fileName = os.path.basename(modelURL)
        self.modelName = fileName[:fileName.index('.')]

        self.cacheDir = './pretrainedModels'
        os.makedirs(self.cacheDir, exist_ok=True)

        get_file(fname=fileName, origin=modelURL, cache_dir=self.cacheDir, cache_subdir='checkpoints',
                 extract=True)

    def loadModel(self):
        print("Loading Model " + self.modelName + '...')
        self.model = tf.saved_model.load(os.path.join(self.cacheDir, 'checkpoints', self.modelName, "saved_model"))

        print("Model " + self.modelName + ' loaded successfully')

    def createBoundingBox(self, image, threshold=0.75):
        inputTensor = cv.cvtColor(image.copy(), cv.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis, ...]

        detections = self.model(inputTensor)

        bboxs = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imgH, imgW, imgC = image.shape

        bboxID = tf.image.non_max_suppression(bboxs, classScores, max_output_size=50,
                                              iou_threshold=threshold, score_threshold=threshold)

        print(bboxID)

        if len(bboxID) != 0:
            for i in bboxID:
                bbox = tuple(bboxs[i].tolist())
                classConfidence = round(100 * classScores[i])
                classIndex = classIndexes[i]

                classLabelText = self.classesList[classIndex].upper()
                classColor = self.colorList[classIndex]

                displayText = '{}: Non-Defective {}%'.format(classLabelText, classConfidence)

                ymin, xmin, ymax, xmax = bbox

                xmin, xmax, ymin, ymax = (xmin*imgW,xmax*imgW,ymin*imgH,ymax*imgH)
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

                cv.rectangle(image,(xmin,ymin), (xmax, ymax), color=classColor, thickness=1)
                cv.putText(image, displayText, (xmin+20, ymin+20), cv.FONT_HERSHEY_PLAIN, 1, classColor, 2)

                #####################BEAUTIFYING-BOUDINGBOX#############################
                lineWidth = min(int((xmax-xmin)*0.2), int((ymax-ymin)*0.2))
                cv.line(image,(xmin,ymin), (xmin+lineWidth,ymin),classColor, thickness=5)
                cv.line(image,(xmin,ymin), (xmin,ymin+lineWidth),classColor, thickness=5)

                cv.line(image, (xmax, ymin), (xmax-lineWidth, ymin), classColor, thickness=5)
                cv.line(image, (xmax, ymin), (xmax, ymin + lineWidth), classColor, thickness=5)

                ############################################
                cv.line(image, (xmin, ymax), (xmin+lineWidth, ymax ), classColor, thickness=5)
                cv.line(image, (xmin, ymax), (xmin, ymax - lineWidth), classColor, thickness=5)

                cv.line(image, (xmax, ymax), (xmax-lineWidth, ymax), classColor, thickness=5)
                cv.line(image, (xmax, ymax), (xmax, ymax - lineWidth), classColor, thickness=5)

        return image

    def predictImage(self, imgPath):
        image = cv.imread(imgPath)
        bboxImage = self.createBoundingBox(image)

        # Storing the detected image
        path = '/Users/shivangchaudhary/PycharmProjects/Recon_Bird_Package/DetectedImages'
        # labelling the image
        timestr = time.strftime("%Y%m%d_%H%M%S")
        # safely storing the image in designated folder
        cv.imwrite(os.path.join(path, "Detected_image_{}.png".format(timestr)), bboxImage)

        # Displaying the detected image
        cv.imshow('Image-Detection ["Q"->Exit]', bboxImage)

        key = cv.waitKey(0) & 0xFF
        if key == ord('q'):
            cv.destroyAllWindows()

    def predictVideo(self, videoPath, threshold):
        cap = cv.VideoCapture(videoPath)

        if cap.isOpened()==False:
            print('Error opening the file...')
            return

        success, img = cap.read()
        startTime = 0

        while success:
            currentTime = time.time()

            fps = 1/(currentTime-startTime)
            startTime = currentTime

            bboxImage = self.createBoundingBox(img, threshold)

            cv.putText(bboxImage, "FPS: "+str(int(fps)), (20,70), cv.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
            # cv.imshow("Result", bboxImage)

            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                cv.destroyAllWindows()