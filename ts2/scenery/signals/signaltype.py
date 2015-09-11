#
#   Copyright (C) 2008-2015 by Nicolas Piganeau
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
import os

import simplejson as json

from ts2.scenery.signals import signalaspect

builtin_signal_aspects = [
    {"name": "BUFFER",
     "linestyle": signalaspect.SignalLineStyle.BUFFER,
     "outershapes": [0, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [0, 0, 0, 0, 0, 0],
     "shapescolors": [0, 0, 0, 0, 0, 0],
     "targets": [1],
     "speedlimits": [0]},
    {"name": "UK_DANGER",
     "linestyle": signalaspect.SignalLineStyle.LINE,
     "outershapes": [0, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [1, 0, 0, 0, 0, 0],
     "shapescolors": ["#FF0000", 0, 0, 0, 0, 0],
     "targets": [1],
     "speedlimits": [0]},
    {"name": "UK_CAUTION",
     "linestyle": signalaspect.SignalLineStyle.LINE,
     "outershapes": [0, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [1, 0, 0, 0, 0, 0],
     "shapescolors": ["#FFFF00", 0, 0, 0, 0, 0],
     "targets": [2],
     "speedlimits": [0]},
    {"name": "UK_PRE_CAUTION",
     "linestyle": signalaspect.SignalLineStyle.LINE,
     "outershapes": [0, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [1, 0, 1, 0, 0, 0],
     "shapescolors": ["#FFFF00", 0, "#FFFF00", 0, 0, 0],
     "targets": [0],
     "speedlimits": [25]},
    {"name": "UK_CLEAR",
     "linestyle": signalaspect.SignalLineStyle.LINE,
     "outershapes": [0, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [1, 0, 0, 0, 0, 0],
     "shapescolors": ["#00FF00", 0, 0, 0, 0, 0],
     "targets": [0],
     "speedlimits": [999]},
    {"name": "FR_TRAM_CLEAR",
     "linestyle": signalaspect.SignalLineStyle.LINE,
     "outershapes": [1, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [20, 0, 0, 0, 0, 0],
     "shapescolors": ["#FFFFFF", 0, 0, 0, 0, 0],
     "targets": [0],
     "speedlimits": [999]},
    {"name": "FR_TRAM_STOP",
     "linestyle": signalaspect.SignalLineStyle.LINE,
     "outershapes": [1, 0, 0, 0, 0, 0],
     "outercolors": [0, 0, 0, 0, 0, 0],
     "shapes": [21, 0, 0, 0, 0, 0],
     "shapescolors": ["#FFFFFF", 0, 0, 0, 0, 0],
     "targets": [1],
     "speedlimits": [0]}
]

builtin_signal_types = [
    {"name": "UK_3_ASPECTS"},
    {"name": "UK_4_ASPECTS"},
    {"name": "UK_3_ASPECTS_JN"},
    {"name": "UK_4_ASPECTS_JN"},
    {"name": "UK_3_ASPECTS_TP"},
    {"name": "UK_4_ASPECTS_TP"},
    {"name": "BUFFER"},
    {"name": "FR_TRAM"}
]

builtin_signal_conditions = [
    {"signaltype": "UK_3_ASPECTS",
     "aspectname": "UK_CLEAR",
     "conditions": 4101,
     "params": {4096: ["UK_CLEAR", "UK_CAUTION", "UK_PRE_CAUTION"]}},
    {"signaltype": "UK_3_ASPECTS",
     "aspectname": "UK_CAUTION",
     "conditions": 4101,
     "params": {4096: ["UK_DANGER", "BUFFER"]}},
    {"signaltype": "UK_3_ASPECTS",
     "aspectname": "UK_DANGER",
     "conditions": 0,
     "params": {4096: []}},

    {"signaltype": "UK_4_ASPECTS",
     "aspectname": "UK_CLEAR",
     "conditions": 4101,
     "params": {4096: ["UK_CLEAR", "UK_PRE_CAUTION"]}},
    {"signaltype": "UK_4_ASPECTS",
     "aspectname": "UK_PRE_CAUTION",
     "conditions": 4101,
     "params": {4096: ["UK_CAUTION"]}},
    {"signaltype": "UK_4_ASPECTS",
     "aspectname": "UK_CAUTION",
     "conditions": 4101,
     "params": {4096: ["UK_DANGER", "BUFFER"]}},
    {"signaltype": "UK_4_ASPECTS",
     "aspectname": "UK_DANGER",
     "conditions": 0,
     "params": {4096: []}},

    {"signaltype": "UK_3_ASPECTS_JN",
     "aspectname": "UK_CLEAR",
     "conditions": 7173,
     "params": {4096: ["UK_CLEAR", "UK_CAUTION"]}},
    {"signaltype": "UK_3_ASPECTS_JN",
     "aspectname": "UK_CAUTION",
     "conditions": 7173,
     "params": {4096: ["UK_DANGER", "BUFFER"]}},
    {"signaltype": "UK_3_ASPECTS_JN",
     "aspectname": "UK_DANGER",
     "conditions": 0,
     "params": {4096: []}},

    # {"signaltype":"UK_4_ASPECTS_JN",
    #  "aspectname":"UK_CLEAR",
    #  "conditions":4101,
    #  "params":{4096:["UK_CLEAR","UK_PRE_CAUTION"]}},
    # {"signaltype":"UK_4_ASPECTS_JN",
    #  "aspectname":"UK_PRE_CAUTION",
    #  "conditions":4101,
    #  "params":{4096:["UK_CAUTION"]}},
    # {"signaltype":"UK_4_ASPECTS_JN",
    #  "aspectname":"UK_CAUTION",
    #  "conditions":4101,
    #  "params":{4096:["UK_DANGER","BUFFER"]}},
    # {"signaltype":"UK_4_ASPECTS_JN",
    #  "aspectname":"UK_DANGER",
    #  "conditions":0,
    #  "params":{4096:[]}},

    {"signaltype": "UK_3_ASPECTS_TP",
     "aspectname": "UK_CLEAR",
     "conditions": 1024,
     "params": {4096: []}},
    {"signaltype": "UK_3_ASPECTS_TP",
     "aspectname": "UK_CAUTION",
     "conditions": 1024,
     "params": {4096: []}},
    {"signaltype": "UK_3_ASPECTS_TP",
     "aspectname": "UK_DANGER",
     "conditions": 0,
     "params": {4096: []}},

    {"signaltype": "UK_4_ASPECTS_TP",
     "aspectname": "UK_CLEAR",
     "conditions": 1024,
     "params": {4096: []}},
    {"signaltype": "UK_4_ASPECTS_TP",
     "aspectname": "UK_PRE_CAUTION",
     "conditions": 1024,
     "params": {4096: []}},
    {"signaltype": "UK_4_ASPECTS_TP",
     "aspectname": "UK_CAUTION",
     "conditions": 1024,
     "params": {4096: []}},
    {"signaltype": "UK_4_ASPECTS_TP",
     "aspectname": "UK_DANGER",
     "conditions": 0,
     "params": {4096: []}},

    {"signaltype": "BUFFER",
     "aspectname": "BUFFER",
     "conditions": 0,
     "params": {4096: []}},

    {"signaltype": "FR_TRAM",
     "aspectname": "FR_TRAM_CLEAR",
     "conditions": 5,
     "params": {4096: []}
     },
    {"signaltype": "FR_TRAM",
     "aspectname": "FR_TRAM_STOP",
     "conditions": 0,
     "params": {4096: []}
     }

]

BUILTIN_SIGNAL_LIBRARY = {
    '__type__': "SignalLibrary",
    'signalAspects': {
        "BUFFER": {
            "__type__": "SignalAspect",
            "lineStyle": signalaspect.SignalLineStyle.BUFFER,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [0, 0, 0, 0, 0, 0],
            "shapesColors": [0, 0, 0, 0, 0, 0],
            "actions": [(signalaspect.Target.BEFORE_THIS_SIGNAL, 0)]
        },
        "UK_DANGER": {
            "__type__": "SignalAspect",
            "lineStyle": signalaspect.SignalLineStyle.LINE,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#FF0000", 0, 0, 0, 0, 0],
            "actions": [(signalaspect.Target.BEFORE_THIS_SIGNAL, 0)]
        },
        "UK_CAUTION": {
            "__type__": "SignalAspect",
            "lineStyle": signalaspect.SignalLineStyle.LINE,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#FFFF00", 0, 0, 0, 0, 0],
            "actions": [(signalaspect.Target.BEFORE_NEXT_SIGNAL, 0)]
        },
        "UK_CLEAR": {
            "__type__": "SignalAspect",
            "lineStyle": signalaspect.SignalLineStyle.LINE,
            "outerShapes": [0, 0, 0, 0, 0, 0],
            "outerColors": [0, 0, 0, 0, 0, 0],
            "shapes": [1, 0, 0, 0, 0, 0],
            "shapesColors": ["#00FF00", 0, 0, 0, 0, 0],
            "actions": [(signalaspect.Target.ASAP, 999)]
        },
    },
    'signalTypes': {
        "BUFFER": {
            "__type__": "SignalType",
            "states": [
                {
                    "__type__": "SignalState",
                    "aspectName": "BUFFER",
                    "conditions": {},
                },
            ]
        },
        "UK_3_ASPECTS": {
            "__type__": "SignalType",
            "states": [
                {
                    "__type__": "SignalState",
                    "aspectName": "UK_CLEAR",
                    "conditions": {
                        "NEXT_ROUTE_ACTIVE": [],
                        "TRAIN_NOT_PRESENT_ON_NEXT_ROUTE": [],
                        "NEXT_SIGNAL_ASPECTS": ["UK_CLEAR", "UK_CAUTION"]
                    }
                },
                {
                    "__type__": "SignalState",
                    "aspectName": "UK_CAUTION",
                    "conditions": {
                        "NEXT_ROUTE_ACTIVE": [],
                        "TRAIN_NOT_PRESENT_ON_NEXT_ROUTE": [],
                        "NEXT_SIGNAL_ASPECTS": ["UK_DANGER", "BUFFER"]
                    }
                },
                {
                    "__type__": "SignalState",
                    "aspectName": "UK_DANGER",
                    "conditions": {},
                },
            ]
        },
    }
}


def json_hook(dct):
    """Hook method for json loading of signal library."""
    if not dct.get('__type__'):
        return dct
    elif dct['__type__'] == "SignalLibrary":
        return SignalLibrary(parameters=dct)
    elif dct['__type__'] == "SignalType":
        return SignalType(parameters=dct)
    elif dct['__type__'] == "SignalState":
        return SignalState(parameters=dct)
    elif dct['__type__'] == "SignalAspect":
        return signalaspect.SignalAspect(parameters=dct)


class ConditionCode:
    """This class holds the possible conditions to display a Signal aspect."""
    # Without parameters
    NEXT_ROUTE_ACTIVE = 1
    PREVIOUS_ROUTE_ACTIVE = 2
    TRAIN_NOT_PRESENT_ON_NEXT_ROUTE = 4
    # With parameters
    TRAIN_NOT_PRESENT_ON_ITEMS = 1024   # No train on any item in list
    ROUTES_SET = 2048                   # At least one route set in list
    NEXT_SIGNAL_ASPECTS = 4096          # Aspect in list


def condition(cls):
    """Decorator to register a class as a condition.

    Conditions are classes which include:
    - A 'code' class attribute
    - A 'solver' function with a signalItem and a params list as parameters. The
    solver function must return True if the signalItem currently meets the
    condition(s) defined by the condition class.
    - A 'properties' class attribute being a list of TIProperty applicable to
    this condition.
    """
    SignalState.solvers[cls.code] = cls.solver
    # SignalState.userParams[conditionName] = userParams
    return cls


@solver("NEXT_ROUTE_ACTIVE")
def next_active_route_solver(signalItem, params=None):
    """This solver returns True if the next route of the signal is active."""
    return bool(signalItem.nextActiveRoute)


@solver("PREVIOUS_ROUTE_ACTIVE")
def previous_active_route_solver(signalItem, params=None):
    """This solver returns True if a route ending at this signal is active."""
    return bool(signalItem.previousActiveRoute)


@solver("TRAIN_NOT_PRESENT_ON_NEXT_ROUTE")
def train_not_present_on_items_solver(signalItem, params=None):
    """This solver returns True if no route is active starting from this signal
    or if there is no train on any items of the active route starting from this
    signal."""
    return not signalItem.trainsAhead()


@solver("TRAIN_NOT_PRESENT_ON_ITEMS")
def train_not_present_on_next_route_solver(signalItem, params=None):
    """This solver returns True if no train is found on any trackItems given
    in the params list. params must be a list of trackItem IDs."""
    if params is None:
        params = []
    simulation = signalItem.simulation
    trackItems = [simulation.trackItem(tiId) for tiId in params]
    if any([ti.trainPresent() for ti in trackItems]):
        return False
    else:
        return True


@solver("ROUTES_SET")
def routes_set_solver(signalItem, params=None):
    """This solver returns True if at least one of the routes given in the
    params list is active. These routes don't have to start at this signal.
    params must be a list of route numbers."""
    if params is None:
        params = []
    simulation = signalItem.simulation
    routes = [simulation.routes[routeNum] for routeNum in params]
    if any([(r.getRouteState() != 0) for r in routes]):
        return True


@solver("NEXT_SIGNAL_ASPECTS")
def next_signals_aspects_solver(signalItem, params=None):
    """This solver returns True if a route starting from this signal is active
    and the ending signal of this route is showing one of the aspects given in
    params. params must be a list of signal aspect names."""
    if params is None:
        params = []
    if signalItem.nextActiveRoute:
        aspectName = signalItem.nextActiveRoute.endSignal.activeAspect.name
        if aspectName in params:
            return True
    return False


class SignalState:
    """A SignalState is an aspect of a signal with a set of conditions to
    display this aspect."""

    def __init__(self, parameters):
        """Constructor for the SignalState class."""
        self.aspect = None
        self.parameters = parameters
        self.conditions = parameters["conditions"]

    def initialize(self, signalLibrary):
        """Initializes the SignalState once we know the SignalState it belongs
        to."""
        if not self.parameters:
            raise Exception("Internal error: SignalState already initialized")
        params = self.parameters
        self.aspect = signalLibrary.signalAspects[params["aspectName"]]
        self.parameters = None

    def for_json(self):
        """Dumps this SignalState to JSON."""
        return {
            "__type__": "SignalState",
            "aspectName": self.aspect.name,
            "conditions": self.conditions
        }

    solvers = {}
    userParams = {}

    def conditionsMet(self, signalItem, params=None):
        """Returns True if all conditions of this SignalState are met (or if
        there is no conditions) on the given signalItem instance."""
        if params is None:
            params = {}
        applicableSolvers = {k: v for (k, v) in SignalState.solvers.items() if
                             k in self.conditions.keys()}
        for conditionName in self.conditions.keys():
            parameters = self.conditions[conditionName]
            parameters.extend(params.get(conditionName, []))
            if not applicableSolvers[conditionName](signalItem, parameters):
                return False
        return True


class SignalType:
    """A SignalType describes a type of signals which can have different
    aspects and the logic for displaying aspects."""

    def __init__(self, parameters):
        """Constructor for the SignalType class."""
        self.name = parameters["name"]
        self.states = parameters["states"]

    def initialize(self, signalLibrary):
        """Initializes this SignalType once the SignalLibrary is loaded."""
        for state in self.states:
            state.initialize(signalLibrary)

    def for_json(self):
        """Dumps this signalType to JSON."""
        return {
            "__type__": "SignalType",
            "name": self.name,
            "states": self.states
        }

    def getDefaultAspect(self):
        """Returns the default aspect for this signal type."""
        return self.states[-1].aspect


class SignalLibrary:
    """A SignalLibrary holds the informations about the signal types and signal
    aspects available in the simulation.

    At runtime, each simulation has SignalLibrary instance which is filled with:
    - The built-in UK_3_ASPECTS  and BUFFER signal types and their aspects
    - The signal types defined in tsl files in the data directory
    - The signal types defined in the simulation itself."""

    def __init__(self, parameters):
        """Constructor for the SignalLibrary class."""
        self.signalAspects = parameters["signalAspects"]
        self.signalTypes = parameters["signalTypes"]
        for st in self.signalTypes:
            st.initialize(self)

    def for_json(self):
        """Dumps this SignalLibrary to JSON."""
        return {
            "__type__": "SignalLibrary",
            "signalAspects": self.signalAspects,
            "signalTypes": self.signalTypes
        }

    def update(self, other):
        """Updates this SignalLibrary instance by adding signal aspects and
        signal types from the other SignalLibrary. If signal aspects or signal
        types of the same name exists in both SignalLibrary instance, the data
        in the other SignalLibray will overwrite the data of this SignalLibrary.
        """
        self.signalAspects.update(other.signalAspects)
        self.signalTypes.update(other.SignalTypes)

    @staticmethod
    def createBuiltinSignalLibrary():
        """Returns a SignalLibrary with the builtin signal types and those
        defined in tsl files in the data directory."""
        builtinLibrary = json.loads(BUILTIN_SIGNAL_LIBRARY,
                                    object_hook=json_hook, encoding="utf-8")
        tslFiles = [f for f in os.listdir("/data") if f.endswith('.tsl')]
        for tslFile in tslFiles:
            with open(tslFile) as fileStream:
                sl = json.load(fileStream, object_hook=json_hook,
                               encoding="utf-8")
                builtinLibrary.update(sl)
        return builtinLibrary
