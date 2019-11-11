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

from overdrive import Overdrive
import random

# Global variables for the cars and the directionchange
# Select which cars to use on the track using MAC address of the device
car2 = Overdrive("CD:5A:27:DC:41:89") #Brandbaar
car3 = Overdrive("DE:83:21:EB:1B:2E") #GAS
#car3 = Overdrive("FB:76:00:CB:82:63") #Explosief
#car3 = Overdrive("DB:DE:FF:52:CB:9E") #Radioactief

direction_car2 = "left"
direction_car3 = "left"

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


def main():
  drive(300)
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  parser.add_argument(
      '--output', help='File path of output file.', required=True)
  args = parser.parse_args()
  
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
