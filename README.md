# autonomousCJ
Self-driving car in GTA San Andreas.

Based on rather simple computer vision techniques, autonomusCJ allows the car to navigate the roads in GTA San Andreas 
by analyzing the location of lanes and edges of the road, as well by extracting information about the roads layout from 
the minimap. 

The collected information about the car's environment is used to calculate the control needed to keep it as close to the 
center of the road as possible.

As the system is in a very early stage of development, implemented control algorithm and road detection are far from 
being perfect. Several problems make detection of characteristic elements on the roads hard, i.e. low-resolution 
textures, blocky shapes of the roads, changing in-game lightning.  

Besides that, for now, I've decided not to use any neural network related algorithms because of my curiosity about how good or 
bad this system can be without using the most obvious solution to the problem. 

## Instalation

1. ```git clone https://github.com/Vatraz/autonomousCJ.git```
2. ```cd autonomousCJ/```
3. ```virtualenv venv```
4. ```source venv/bin/activate```
5. ```pip3 install -r requirements.txt```
6. ```python3 main.py```

## Usage

Run the script ```python main.py``` with GTA:SA running in a window mode in 800x600 resolution and placed in the top-left corner of the screen. Then it is necessary to get into any car, toggle camera to the bumper cam and drive 
to any road in the position that will be maintained by algorithm. After that, press "G" to start.
