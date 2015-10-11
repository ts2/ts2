Quick Code Guide
======================================

.. note::
    This guide is work in progress.

Here's a brief rundown of the source. This is not extensive, but a quick brief on where
things are and what they do, so u can get the concept of how it works.

Also note that this quide is written against ``develop`` branch, so some stuff is
probably incorrect as the project moves forward.

Data
--------------
- From ``v0.6`` and current develop branch, simulation data is stored in json. (no more sqlite).
- Simulation data is also saved/shared in the `ts2-data <https://github.com/ts2/ts2-data>`_ repository.



Startup
--------------
- Running  ``start-ts2.py`` starts the application in :func:`~ts2.application.Main`
- which presents the :class:`~ts2.mainwindow.MainWindow`
- A file is opened with the :class:`~ts2.gui.opendialog.OpenDialog`
- and a :class:`~ts2.simulation.Simulation` is loaded in :func:`~ts2.mainwindow.MainWindow.loadSimulation`


Track Items
-------------------
Track items are objects and scenery within the simulation, such as:

- :class:`~ts2.scenery.lineitem.LineItem` - a simple 'track' used to connect other item
- :class:`~ts2.scenery.pointsitem.PointsItem` - a three way junction
- :class:`~ts2.scenery.platformitem.PlatformItem` - a colored rectangle to symbolise a platform
- :class:`~ts2.scenery.signals.signalitem.SignalItem` - a signal of - :class:`~ts2.scenery.signals.signalitem.SignalType`
- :class:`~ts2.scenery.textitem.TextItem` - display some text on layout
- :class:`~ts2.scenery.invisiblelinkitem.InvisibleLinkItem` - as line, but not shown on scenery

The **base** for most track items is the abstract  :class:`~ts2.scenery.abstract.TrackItem` class.


Signals
-------------------
- :class:`~ts2.scenery.signals.signalitem.SignalItem`  represents a :class:`~ts2.scenery.signals.signalitem.SignalType`




