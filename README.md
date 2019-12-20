# Git of the racetrackdemo
* Recognizes 4 signs of dangerous chemicals that are located on the rear of ANKI overdrive cars. Presents the results in a streamlit dashboard

### Git clone
* `git clone git@git.intranet.rws.nl:Datalab/workshops/tutorials/racebaan_adr.git`
* `cd racebaan_adr`

### Build Conda environment from .yml file
* `conda env create -f ADRenvironment.yml`

### Activate environment
* `conda activate ADRdemo`

### Install tflite using wheel file
* You can skip this step if cloning on Linux x86_64 
* https://www.tensorflow.org/lite/guide/python.
* Choose Python 3.7 version that matches your system
* Install with:
* `python3.7 -m pip install wheelbestand`

### Install Bluepy
* `sudo apt-get install python3-pip libglib2.0-dev`
* `python3.7 -m pip install bluepy --user`

### Open new tab/terminal with the same environment
* In new tab/terminal:
* `conda activate ADRdemo`

### Building of track
* Make an 'oval' track with 2x 2 straight pieces with 2x 2 corner pieces. Track starts with straight piece 34 (start/finish), then straight piece 39, 2x corner 20, straigh 36, straight 40 and 2 corner 18. Bridge with webcam at the end of the second corner 20 and the beginning of the straight 36. Point webcam to straight piece. Cars should drive in the same direction as track layout above.

### Run recognitionmodel
* `python ADRmodel.py --model ADRmodel.tflite --labels ADRlabels.txt --output ADRoutput.csv --mode ADR`
* Cars start driving and webcamscreen opens. If labels are recognized with more than 90% certainty, the results are stored in ADRoutput.csv and visualized in the dash dashboard. Change lat lon coordinates in ADRmodel.py to make the recognition at the correct place (https://www.latlong.net/).

### Or run object detection model
*`python ADRmodel.py --model ADRmodel.tflite --labels ADRlabels.txt --output ADRoutput.csv --mode object`

### Inputspeed can be set with --input_speed XXX
* XXX is an integer between 200 en 800. Determines speed of the cars.

### Visualization in two dashboards
`python dash_racebaan.py` for a dashboard with the recognized ADR labels. Gives map with point to show where the labels are recognized and bar chart to show what is recognized on which side of the road.
`python dash_with_testdata.py` for a dashboard with more data. Uses a proxy-dataset and gives a map that shows the intensity of the Dutch highways and a bar chart for selected points. 

### Driving without any other recognition
`python just_drive.py` Two cars start driving and nothing else happens.


