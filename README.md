# TS2 - Train Signalling Simulation

## Overview
"Train Signalling Simulation" (TS2) is a simulation game where you have to dispatch trains across an area and keep them on schedule. See homepage for more details.

## Links
* [TS2 Homepage](http://ts2.sf.net)
* [TS2 Project page at SourceForge.net](http://sourceforge.net/projects/ts2/)
* [TS2 devel page on GitHub](https://gihub.com/npiganeau/ts2)

## Status
TS2 Train Signalling Simulation is beta software, meaning it is playable, but lacks many features that one would expect from a simulation.
A demo simulation called "drain" can be found in the _data_ directory.

## Installation
* Released versions: Unzip the file to a suitable location and run ts2.exe
* Development versions:
    - Download and install Python v3 or above at [www.python.org](http://www.python.org)
    - Download and install PyQt v4.8 or above at [http://www.riverbankcomputing.co.uk](http://www.riverbankcomputing.co.uk)
    - Grab the sources from GitHub
    - Run ts2/application.py

## Playing (QuickStart)
* Load the demo simulation "drain.ts2" in the "data" directory.
* Route setting:
    - To turn a signal from red to green, you need to set a route from this signal to the next one.
    - To set a route left click on the signal and then to the next one. If you can create a route
        between these signals, the track between both signals is highlighted in white, the points are
        turned automatically for this route and the first signal color turn to yellow (or green if 
        the second signal is already yellow).
    - To cancel a route, right-click on its first signal.
    - Routes are automatically cancelled by the first train passing through. However, you can set a
        persistent route by holding the shift key before clicking on the second signal. Persistent 
        routes have a little white square next to their first signal.
* Train information:
    - Click on a train code on the scene or on the train list to see its information on the 
        "Train Information" window. The "Service information" window will also update.
* Station information:
    - Click on a platform on the scene to display the station timetable in the "Station information" 
        window.
* Interact with trains:
    - Right click on a train code on the scene or on the "Train information" or on the "Train List"
    window to display the train menu. This menu enables you to:
        + Assign a new service to this train. Select the service in the popup window and click "Ok".
        + Reset the service. i.e. tell the train driver to stop at the first station again.
        + Reverse train. i.e. change the train direction.
    - Trains automatically change service when it is over (on drain demo BW01 becomes WB01 when reaching 
    depot) 
* You should see trains run, stop at red signals and at scheduled stations. They should depart at the 
    departure time or 30 seconds after the arrival time if the departure time is past (parameter for Drain
    demo simulation).   

## File format
The ts2 files are in fact sqlite3 databases. 
One ts2 file holds all the information for a simulation.
See the [How to create your own Simulation](http://ts2.sourceforge.net/create_simulations.pdf) documentation for database format.

## Known bugs
- When reversing a train, the previous route is not cancelled, and the track remains highlighted.
- When running with simulation speeds above 5x, trains sometime overtake red signals. 

## Roadmap
The objective for next version (0.3) is to have an integrated graphical editor so that users can easily create their own simulations.

