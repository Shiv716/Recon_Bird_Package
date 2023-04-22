from Detector import *

# Model to be used in the project
modelURL = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz'

# Back-up models
# modelURL = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/efficientdet_d4_coco17_tpu-32.tar.gz'
#modelURL='http://download.tensorflow.org/models/object_detection/tf2/20200711/faster_rcnn_resnet101_v1_640x640_coco17_tpu-8.tar.gz'

threshold = 0.75


# Following file contains 92 classes built in that can be detected by the models.
classFile = 'coco.names'
detector = Detector()
detector.readClasses(classFile)
detector.downloadModel(modelURL)
detector.loadModel()
#detector.predictVideo(0, threshold)
detector.predictImage('test2.jpeg')