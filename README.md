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

### Run recognitionmodel
* `python ADRmodel.py --model ADRmodel.tflite --labels ADRlabels.txt --output ADRoutput.csv --mode ADR`
* Cars start driving and webcamscreen opens. If labels are recognized with more than 90% certainty, the results are stored in ADRoutput.csv and visualized in the streamlit dashboard.

### Or run object detection model
*`python ADRmodel.py --model ADRmodel.tflite --labels ADRlabels.txt --output ADRoutput.csv --mode object`

### Inputspeed can be set with --input_speed XXX
* XXX is an integer between 200 en 800. Determines speed of the cars.

### Open streamlit in other tab
* `streamlit run ADRstreamlit.py`
* Latlon coordinates can be changed if the demo is not in Utrecht
* Runs best in Firefox

### Building of track
* Make an 'oval' track with 2x 2 straight pieces with 2x 2 corner pieces. Track starts with straight piece 34 (start/finish), then straight piece 39, 2x corner 20, straigh 36, straight 40 and 2 corner 18. Bridge with webcam at the end of the second corner 20 and the beginning of the straight 36. Point webcam to straight piece. Cars should drive in the same direction as track layout above.
