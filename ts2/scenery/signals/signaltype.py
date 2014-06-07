#
#   Copyright (C) 2008-2014 by Nicolas Piganeau
#   npi@m4x.org
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from PyQt4 import QtCore

from ts2.scenery.signals import signalaspect

builtin_signal_aspects = [
    {"name":"BUFFER",
     "linestyle":signalaspect.SignalLineStyle.BUFFER,
     "outershapes":[0,0,0,0,0,0],
     "outercolors":[0,0,0,0,0,0],
     "shapes":[0,0,0,0,0,0],
     "shapescolors":[0,0,0,0,0,0],
     "targets":[1],
     "speedlimits":[0]},
    {"name":"UK_DANGER",
     "linestyle":signalaspect.SignalLineStyle.LINE,
     "outershapes":[0,0,0,0,0,0],
     "outercolors":[0,0,0,0,0,0],
     "shapes":[1,0,0,0,0,0],
     "shapescolors":["#FF0000",0,0,0,0,0],
     "targets":[1],
     "speedlimits":[0]},
    {"name":"UK_CAUTION",
     "linestyle":signalaspect.SignalLineStyle.LINE,
     "outershapes":[0,0,0,0,0,0],
     "outercolors":[0,0,0,0,0,0],
     "shapes":[1,0,0,0,0,0],
     "shapescolors":["#FFFF00",0,0,0,0,0],
     "targets":[2],
     "speedlimits":[0]},
    {"name":"UK_PRE_CAUTION",
     "linestyle":signalaspect.SignalLineStyle.LINE,
     "outershapes":[0,0,0,0,0,0],
     "outercolors":[0,0,0,0,0,0],
     "shapes":[1,0,1,0,0,0],
     "shapescolors":["#FFFF00",0,"#FFFF00",0,0,0],
     "targets":[0],
     "speedlimits":[25]},
    {"name":"UK_CLEAR",
     "linestyle":signalaspect.SignalLineStyle.LINE,
     "outershapes":[0,0,0,0,0,0],
     "outercolors":[0,0,0,0,0,0],
     "shapes":[1,0,0,0,0,0],
     "shapescolors":["#00FF00",0,0,0,0,0],
     "targets":[0],
     "speedlimits":[999]}
]

builtin_signal_types = [
    {"name":"UK_3_ASPECTS"},
    {"name":"UK_4_ASPECTS"},
    {"name":"BUFFER"}
]

builtin_signal_conditions = [
    {"signaltype":"UK_3_ASPECTS",
     "aspectname":"UK_CLEAR",
     "conditions":4101,
     "params":{4096:["UK_CLEAR","UK_CAUTION"]}},
    {"signaltype":"UK_3_ASPECTS",
     "aspectname":"UK_CAUTION",
     "conditions":4101,
     "params":{4096:["UK_DANGER","BUFFER"]}},
    {"signaltype":"UK_3_ASPECTS",
     "aspectname":"UK_DANGER",
     "conditions":0,
     "params":{4096:[]}},

    {"signaltype":"UK_4_ASPECTS",
     "aspectname":"UK_CLEAR",
     "conditions":4101,
     "params":{4096:["UK_CLEAR","UK_PRE_CAUTION"]}},
    {"signaltype":"UK_4_ASPECTS",
     "aspectname":"UK_PRE_CAUTION",
     "conditions":4101,
     "params":{4096:["UK_CAUTION"]}},
    {"signaltype":"UK_4_ASPECTS",
     "aspectname":"UK_CAUTION",
     "conditions":4101,
     "params":{4096:["UK_DANGER","BUFFER"]}},
    {"signaltype":"UK_4_ASPECTS",
     "aspectname":"UK_DANGER",
     "conditions":0,
     "params":{4096:[]}},

    {"signaltype":"BUFFER",
     "aspectname":"BUFFER",
     "conditions":0,
     "params":{4096:[]}}
]

class ConditionCode:
    """This class holds the possible conditions to display a Signal aspect."""
    # Without parameters
    NEXT_ROUTE_ACTIVE = 1
    PREVIOUS_ROUTE_ACTIVE = 2
    TRAIN_NOT_PRESENT_ON_NEXT_ROUTE = 4
    # With parameters
    TRAIN_PRESENT_ON_ITEMS = 1024
    ROUTES_SET = 2048
    NEXT_SIGNAL_ASPECTS = 4096

class SignalCondition:
    """A SignalCondition is the concatenation of an aspect with set of
    conditions and parameters to display this aspect."""

    def __init__(self, aspect, code, params):
        """Constructor for the SignalCondition class."""
        self.aspect = aspect
        self.conditionCode = code
        self.params = params

class SignalType(QtCore.QObject):
    """A SignalType describes a type of signals which can have different
    aspects and the logic for displaying aspects."""

    def __init__(self, name):
        """Constructor for the SignalType class."""
        super().__init__()
        self.name = name
        self.conditions = []

    def addCondition(self, condition):
        """Adds the SignalCondition given to the conditions list of the
        signal type."""
        self.conditions.append(condition)

    def getDefaultAspect(self):
        """Returns the default aspect for this signal type."""
        return self.conditions[-1].aspect

    @staticmethod
    def createBuiltinSignalLibrary():
        """Returns a Signal type dict of builtin signal types."""
        saLibrary = {}
        stLibrary = {}
        for sa in builtin_signal_aspects:
            saLibrary[sa["name"]] = signalaspect.SignalAspect(sa)
        for st in builtin_signal_types:
            stLibrary[st["name"]] = SignalType(st["name"])
        for sc in builtin_signal_conditions:
            cond = SignalCondition(saLibrary[sc["aspectname"]],
                                   sc["conditions"],
                                   sc["params"])
            stLibrary[sc["signaltype"]].addCondition(cond)
        return stLibrary

