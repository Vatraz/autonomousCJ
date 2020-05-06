# autonomousCJ
Self-driving car in GTA San Andreas.

Based on rather simple computer vision techniques, autonomusCJ analyzes the arrangement of lanes/edges of the road and extracts information about the roads layout from 
the minimap. 

The collected information about the car environment is used to calculate the control needed to keep it as close to the 
center of the road as possible.

[![](https://i.postimg.cc/DwPbN8fr/screenshot-from-2020-03-30-04.jpg)](https://youtu.be/FfvnZxzQvY4)

## Instalation

1. ```git clone https://github.com/Vatraz/autonomousCJ.git```
2. ```cd autonomousCJ/```
3. ```virtualenv venv```
4. ```source venv/bin/activate```
5. ```pip install -r requirements.txt```
6. ```python main.py```

## Usage

Run the script ```main.py``` with GTA:SA running in a window mode in 800x600 resolution and placed in the top-left corner of the screen. Then get into any car, toggle camera to the bumper cam, and press the spacebar to start.
