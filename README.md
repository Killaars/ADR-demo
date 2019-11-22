# Git voor de racebaandemo
* Herkent automatisch 4 gevaarlijke stoffen stickers die achterop ANKI overdrive autos geplakt zijn en vat de resultaten samen in een streamlit dashboard.

### Git clone
* `git clone git@git.intranet.rws.nl:Datalab/workshops/tutorials/racebaan_adr.git`
* `cd racebaan_adr`

### Bouwen Conda environment met de .yml file
* `conda env create -f ADRenvironment.yml`

### Activeer environment
* `conda activate ADRdemo`

### Installeren tflite via wheel bestand
* Indien je op linux x86_64 draait kan je dit overslaan
* https://www.tensorflow.org/lite/guide/python.
* Kies de Python 3.7 versie die bij jouw systeem hoort.
* eventueel installeren met:
* `python3.7 -m pip install wheelbestand`

### Installeren Bluepy
* sudo apt-get install python3-pip libglib2.0-dev
* python3.7 -m pip install bluepy --user

### Downloaden model
* Download van de flashblade (lars_data/adr/ADRmodel.tflite) of vraag aan Lars. Zet het in deze map
* Kleiner testmodel (mobilenet2.tflite) zit in de repository

### Open nieuwe tab met dezelfde environment

### Draai herkenningsmodel
* `python ADRmodel.py --model ADRmodel.tflite --labels ADRlabels.txt --output ADRoutput.csv`
* Auto's gaan rijden en webcamscherm opent. Indien auto's met meer dan 90% zekerheid herkent worden, worden de resultaten in ADRoutput.csv weggeschreven en gevisualiseerd in het streamlit dashboard.

### Open streamlit in de andere tab
* `streamlit run ADRstreamlit.py`
* Eventueel latlon coordinaten aanpassen als demo niet in Utrecht gedraaid wordt.
* werkt het beste in firefox merk ik

### Opbouwen racebaan
* Maak een 'ovaal' van 2x 2 rechte stukken afgewisseld door 2x 2 bochten aan elkaar. Rondje begint met recht stuk 34 (start/finish), daarna recht stuk 39, 2x bocht 20, recht stuk 36, recht stuk 40 en 2 bochten 18. Brug met webcam op het einde van de laatste bocht 20 en het begin van rechte stuk 36. Webcam gericht op het rechte stuk. Auto's in dezelfde richting laten rijden als hierboven beschreven. 







