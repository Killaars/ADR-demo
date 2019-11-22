from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import datetime
import pandas as pd
import numpy as np
import os
import cv2
from tflite_runtime.interpreter import Interpreter
import six.moves.urllib as urllib
import tarfile
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util

from overdrive import Overdrive
import random

# Global variables for the cars and the directionchange
# Select which cars to use on the track using MAC address of the device
car2 = Overdrive("CD:5A:27:DC:41:89") #Brandbaar
#car3 = Overdrive("DE:83:21:EB:1B:2E") #GAS
car3 = Overdrive("FB:76:00:CB:82:63") #Explosief
#car3 = Overdrive("DB:DE:FF:52:CB:9E") #Radioactief

direction_car2 = "left"
direction_car3 = "left"

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the
# object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')
NUM_CLASSES = 90

def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]

def save_pred(fname, label, lat, lon, road):
    timestamp = [pd.Timestamp(datetime.datetime.now())]
    df = pd.DataFrame({'lat':lat,
                   'lon':lon,
                   'road':road,
                   'gevi':label,
                   'timestamp':timestamp},index=[0])
    with open(str(fname), 'a') as f:
        df.to_csv(f, header=f.tell()==0)
        f.close()
        
def locationChangeCallback(addr, location, piece, speed, clockwise):
    # Print out addr, piece ID, location ID of the vehicle, this print
    # everytime when location changed
    print("Location from " + addr + " : " + "Piece=" + str(piece) +
          " Location=" + str(location) + " Clockwise=" + str(clockwise))
    print(piece)

    # Autos wisselen op hetzelfde moment
    """
    if piece == 18:
        print('change')
        car3.changeLaneRight(1000, 1000)
        car2.changeLaneRight(1000, 1000)
        #car3.changeSpeed(1000, 1000)
    if piece == 23:
        print('change')
        car3.changeLaneLeft(1000, 1000)
        car2.changeLaneLeft(1000, 1000)
    if piece == 40:
        print('change')
        car3.changeLaneLeft(1000, 1000)
        car2.changeLaneLeft(1000, 1000)
    """
    #if piece == 34:
     #   car3.changeSpeed(0, 1000)
        
def drive(input_speed):
       # Set initial car speed and acceleration for the two cars
       initial_car_speed = input_speed
       initial_car_acceleration = 800
       car2.changeSpeed(initial_car_speed, initial_car_acceleration)
       car3.changeSpeed(initial_car_speed, initial_car_acceleration)
       
       car2.setLocationChangeCallback(locationChangeCallback_car2)
       car3.setLocationChangeCallback(locationChangeCallback_car3)
    
def locationChangeCallback_car2(addr, location, piece, speed, clockwise):
    # Print out addr, piece ID, location ID of the vehicle, this print
    # everytime when location changed
    #print("Location from " + addr + " : " + "Piece=" + str(piece) +
    #      " Location=" + str(location) + " Clockwise=" + str(clockwise))
    #print(piece)
    if piece ==34:
        switch = random.random()
        global direction_car2
        if switch>0.7:
            direction_car2="left"
        else:
            direction_car2="right"
    if direction_car2 == "left":
        if piece == 40:
            car2.changeLaneRight(1000, 1000)    
        if piece == 18:
            car2.changeLaneRight(1000, 1000)
        if piece == 39:
            car2.changeLaneLeft(1000, 1000)
        if piece == 20:
            car2.changeLaneLeft(1000, 1000)
    elif direction_car2 =="right":
        if piece == 40:
            car2.changeLaneLeft(1000, 1000)    
        if piece == 18:
            car2.changeLaneLeft(1000, 1000)
        if piece == 39:
            car2.changeLaneRight(1000, 1000)
        if piece == 20:
            car2.changeLaneRight(1000, 1000)
            
def locationChangeCallback_car3(addr, location, piece, speed, clockwise):
    # Print out addr, piece ID, location ID of the vehicle, this print
    # everytime when location changed
    #print("Location from " + addr + " : " + "Piece=" + str(piece) +
    #      " Location=" + str(location) + " Clockwise=" + str(clockwise))
    #print(piece)
    if piece ==34:
        switch = random.random()
        global direction_car3
        if switch>0.3:
            direction_car3="left"
        else:
            direction_car3="right"
    if direction_car3 == "left":
        if piece == 40:
            car3.changeLaneRight(1000, 1000)    
        if piece == 18:
            car3.changeLaneRight(1000, 1000)
        if piece == 39:
            car3.changeLaneLeft(1000, 1000)
        if piece == 20:
            car3.changeLaneLeft(1000, 1000)
    elif direction_car3 =="right":
        if piece == 40:
            car3.changeLaneLeft(1000, 1000)    
        if piece == 18:
            car3.changeLaneLeft(1000, 1000)
        if piece == 39:
            car3.changeLaneRight(1000, 1000)
        if piece == 20:
            car3.changeLaneRight(1000, 1000)


def main(input_speed=300):
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  parser.add_argument(
      '--output', help='File path of output file.', required=True)
  parser.add_argument(
      '--mode', help='mode for the model.', required=False, default = 'ADR')
  parser.add_argument(
      '--input_speed', help='speed of the model.', required=False, default=300)
  args = parser.parse_args()
  
  
  drive(int(input_speed))
  
  if args.mode == 'ADR':
      ADRmain(args)
  else:
      cocomain(input_speed)
      
def cocomain(input_speed):
    initial_car_acceleration = 800
    if not os.path.exists(MODEL_NAME + '/frozen_inference_graph.pb'):
    	print ('Downloading the model')
    	opener = urllib.request.URLopener()
    	opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
    	tar_file = tarfile.open(MODEL_FILE)
    	for file in tar_file.getmembers():
    	  file_name = os.path.basename(file.name)
    	  if 'frozen_inference_graph.pb' in file_name:
    	    tar_file.extract(file, os.getcwd())
    	print('Download complete')
    else:
    	print('Model already exists')

    # ## Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    # Loading label map:
    # Label maps map indices to category names, so that when our convolution
    # network predicts `5`, we know that this corresponds to `airplane`.  Here
    # we use internal utility functions, but anything that returns a dictionary
    # mapping integers to appropriate string labels would be fine

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    # Intializing the web camera device: 0 for internal and 1 for external camera
    # of the laptop used
    cap = cv2.VideoCapture(0)

    # Running the tensorflow session
    with detection_graph.as_default():
      with tf.Session(graph=detection_graph) as sess:
       ret = True
       while (ret):
          ret,image_np = cap.read()
          #print(image_np)
          # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
          image_np_expanded = np.expand_dims(image_np, axis=0)
          #print(image_np_expanded)
          image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
          # Each box represents a part of the image where a particular object was detected.
          boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
          # Each score represent how level of confidence for each of the objects.
          # Score is shown on the result image, together with the class label.
          scores = detection_graph.get_tensor_by_name('detection_scores:0')
          classes = detection_graph.get_tensor_by_name('detection_classes:0')
          num_detections = detection_graph.get_tensor_by_name('num_detections:0')
          # Actual detection.
          (boxes, scores, classes, num_detections) = sess.run(
              [boxes, scores, classes, num_detections],
              feed_dict={image_tensor: image_np_expanded})
          # Visualization of the results of a detection.
          vis_util.visualize_boxes_and_labels_on_image_array(
              image_np,
              np.squeeze(boxes),
              np.squeeze(classes).astype(np.int32),
              np.squeeze(scores),
              category_index,
              use_normalized_coordinates=True,
              line_thickness=8)
          classes_detected = classes[scores>0.5]
          if 13 in classes_detected:
              #print('detected')
              car3.changeSpeed(0, initial_car_acceleration)
              car2.changeSpeed(0, initial_car_acceleration)
              #car3.changeLaneRight(250, 250)
              car3.setLocationChangeCallback(locationChangeCallback)
              #print(car3.piece)
          elif 10 in classes_detected:
              print('verkeerslicht detected')
              #print('detected')
              car3.changeSpeed(0, initial_car_acceleration)
              car2.changeSpeed(0, initial_car_acceleration)
              #car3.changeLaneRight(250, 250)
              car3.setLocationChangeCallback(locationChangeCallback)
              """
          elif 1 in classes_detected:
              print('car detected')
              car3.changeSpeed(int(initial_car_speed/2), initial_car_acceleration)
              car2.changeSpeed(int(initial_car_speed/2), initial_car_acceleration)
              car3.setLocationChangeCallback(locationChangeCallback)
              """
          else:
              car3.changeSpeed(input_speed, initial_car_acceleration)
              car2.changeSpeed(input_speed, initial_car_acceleration)
              car3.setLocationChangeCallback(locationChangeCallback)
              #print(car3.piece)
              #drive(cv2)
          #print(image_np,boxes,classes,scores,category_index)
          #plt.figure(figsize=IMAGE_SIZE)
          #plt.imshow(image_np)
          cv2.imshow('image',cv2.resize(image_np,(1280,960)))
          if cv2.waitKey(25) & 0xFF == ord('q'):
              cv2.destroyAllWindows()
              cap.release()
              break

def ADRmain(args):
  # Load labels
  labels = load_labels(args.labels)
  
  # Create dict with time of last recognition
  savetimes=dict()
  for key in labels:
      print(labels[key])
      savetimes[labels[key]] = datetime.datetime.now()
 
  # Load model
  interpreter = Interpreter(args.model)
  interpreter.allocate_tensors()
  _, height, width, _ = interpreter.get_input_details()[0]['shape']
  
  # Load outputpath and clear file
  fname = args.output
  try:
      os.remove(fname)
      print('removing output')
  except: 
      print('no previous output')
  lat = [52.058846]
  lon = [5.101712]
    
  cap = cv2.VideoCapture(0)
  cap.set(3,1280)
  cap.set(4,1280)
  ret=True
  while (ret):
    ret,image = cap.read()
    # transform image to RGB and slice in half. Then rescale to 320x320
    imageout = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image=image/255
    image = image[320:,:]
    imageleft = image[:,:640]
    imageright = image[:,640:]
    if args.model=='mobilenet.tflite':
        print('mobilenet')
        imageleft = cv2.resize(imageleft,(224,224))
        imageright = cv2.resize(imageright,(224,224))
        
    else:
        imageleft = cv2.resize(imageleft,(320,320))
        imageright = cv2.resize(imageright,(320,320))

    #predict stuff
    resultsleft = classify_image(interpreter, imageleft)
    resultsright = classify_image(interpreter, imageright)
    
    label_idleft, probleft = resultsleft[0]
    label_idright, probright = resultsright[0]
    labelleft = labels[label_idleft]
    labelright = labels[label_idright]
    
    # write stuff if prob>threshold
    for label,prob,road in zip([labelleft,labelright],[probleft,probright],['left','right']):
        if prob>0.9:
            if (datetime.datetime.now()-savetimes[label]).total_seconds()>5:
                if label != 'Niks':
                    print(road,': ',label,' ',prob)
                    print(road,'saving')
                    savetimes[label] = datetime.datetime.now()
                    save_pred(fname,label,lat,lon,road)
        
    

    cv2.imshow('image',imageout)
    if cv2.waitKey(25) & 0xFF == ord('q'):
      cv2.destroyAllWindows()
      cap.release()
      break


if __name__ == '__main__':
    
  main()
