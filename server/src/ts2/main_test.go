package ts2

import (
	"testing"
)

func (a DelayGenerator) equals(b DelayGenerator) bool {
	for i := 0; i < len(a.data); i++ {
		for j := 0; j < 3; j++ {
			if a.data[i][j] != b.data[i][j] {
				return false
			}
		}
	}
	return true
}

func assertTrue(t *testing.T, expr bool, msg string) {
	if !expr {
		t.Errorf("%v: expression is false", msg)
	}
}

func assertEqual(t *testing.T, a interface{}, b interface{}, msg string) {
	if a != b {
		t.Errorf("%v: %v(%T) is not equal to %v(%T)", msg, a, a, b, b)
	}
}

const simJson string = `
{
	"__type__": "Simulation",
	"messageLogger": {
		"__type__": "MessageLogger",
		"messages": []
	},
	"options": {
		"currentScore": 12,
		"currentTime": "06:00:00",
		"defaultDelayAtEntry": 0,
		"defaultMaxSpeed": 18.06,
		"defaultMinimumStopTime": [[20,40,90],[40,120,10]],
		"defaultSignalVisibility": 100,
		"description": "This simulation is a demo sim !",
		"timeFactor": 5,
		"title": "Demo Sim",
		"trackCircuitBased": false,
		"warningSpeed": 8.34,
		"version": "0.7"
	},
	"routes": {
		"1": {
			"__type__": "Route",
			"beginSignal": 72,
			"directions": {
				"511": 0,
				"512": 0
			},
			"endSignal": 73,
			"initialState": 1,
			"routeNum": 1
		}
	},
	"trackItems": {
        "1": {
            "__type__": "EndItem",
            "conflictTiId": null,
            "maxSpeed": 27.77,
            "name": null,
            "nextTiId": null,
            "previousTiId": 2,
            "x": 0.0,
            "y": 0.0
		},
        "2": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 27.77,
            "name": null,
            "nextTiId": 3,
            "placeCode": "LFT",
            "previousTiId": 1,
            "realLength": 400.0,
            "trackCode": null,
            "x": 0.0,
            "xf": 90.0,
            "y": 0.0,
            "yf": 0.0
        },
        "3": {
            "__type__": "SignalItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "31",
            "nextTiId": 2,
            "previousTiId": 4,
            "reverse": true,
            "signalType": "UK_3_ASPECTS",
            "x": 100.0,
            "xn": 105.0,
            "y": 0.0,
            "yn": 5.0
        },
        "4": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "Sample Name",
            "nextTiId": 5,
            "placeCode": null,
            "previousTiId": 3,
            "realLength": 400.0,
            "trackCode": null,
            "x": 100.0,
            "xf": 190.0,
            "y": 0.0,
            "yf": 0.0
        },
        "5": {
            "__type__": "SignalItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "32",
            "nextTiId": 6,
            "previousTiId": 4,
            "reverse": false,
            "signalType": "UK_3_ASPECTS",
            "x": 190.0,
            "xn": 195.0,
            "y": 0.0,
            "yn": 5.0
        },
        "6": {
            "__type__": "InvisibleLinkItem",
            "conflictTiId": null,
            "maxSpeed": 10.0,
            "name": null,
            "nextTiId": 7,
            "placeCode": null,
            "previousTiId": 5,
            "realLength": 200.0,
            "trackCode": null,
            "x": 200.0,
            "xf": 245.0,
            "y": 0.0,
            "yf": 0.0
        },
        "7": {
            "__type__": "PointsItem",
            "conflictTiId": null,
            "maxSpeed": 10.0,
            "name": null,
            "nextTiId": 8,
            "previousTiId": 6,
            "reverseTiId": 14,
            "x": 250.0,
            "xf": -5.0,
            "xn": 5.0,
            "xr": 5.0,
            "y": 0.0,
            "yf": 0.0,
            "yn": 0.0,
            "yr": 5.0
		},
        "8": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 10.0,
            "name": null,
            "nextTiId": 9,
            "placeCode": null,
            "previousTiId": 7,
            "realLength": 200.0,
            "trackCode": null,
            "x": 255.0,
            "xf": 290.0,
            "y": 0.0,
            "yf": 0.0
        },
        "9": {
            "__type__": "SignalItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "33",
            "nextTiId": 8,
            "previousTiId": 10,
            "reverse": true,
            "signalType": "UK_3_ASPECTS",
            "x": 300.0,
            "xn": 305.0,
            "y": 0.0,
            "yn": 5.0
        },
        "10": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": 11,
            "placeCode": "STN",
            "previousTiId": 10,
            "realLength": 400.0,
            "trackCode": "1",
            "x": 300.0,
            "xf": 390.0,
            "y": 0.0,
            "yf": 0.0
        },
        "11": {
            "__type__": "SignalItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "34",
            "nextTiId": 12,
            "previousTiId": 10,
            "reverse": false,
            "signalType": "UK_3_ASPECTS",
            "x": 390.0,
            "xn": 395.0,
            "y": 0.0,
            "yn": 5.0
        },
        "12": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": 11,
            "placeCode": "RGT",
            "previousTiId": 10,
            "realLength": 400.0,
            "trackCode": null,
            "x": 400.0,
            "xf": 500.0,
            "y": 0.0,
            "yf": 0.0
        },
        "13":{
            "__type__": "EndItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": null,
            "previousTiId": 12,
            "x": 500.0,
            "y": 0.0
		},
        "14": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 10.0,
            "name": null,
            "nextTiId": 115,
            "placeCode": null,
            "previousTiId": 7,
            "realLength": 200.0,
            "trackCode": null,
            "x": 255.0,
            "xf": 280.0,
            "y": 5.0,
            "yf": 25.0
        },
        "15": {
            "__type__": "SignalItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "35",
            "nextTiId": 14,
            "previousTiId": 16,
            "reverse": true,
            "signalType": "UK_3_ASPECTS",
            "x": 290.0,
            "xn": 295.0,
            "y": 25.0,
            "yn": 30.0
        },
        "16": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": 17,
            "placeCode": "STN",
            "previousTiId": 15,
            "realLength": 400.0,
            "trackCode": "2",
            "x": 290.0,
            "xf": 390.0,
            "y": 25.0,
            "yf": 25.0
        },
        "17": {
            "__type__": "SignalItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": 18,
            "previousTiId": 16,
            "reverse": false,
            "signalType": "BUFFER",
            "x": 390.0,
            "xn": 395.0,
            "y": 25.0,
            "yn": 30.0
        },
        "18": {
            "__type__": "EndItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": null,
            "previousTiId": 17,
            "x": 400.0,
            "y": 0.0
		},
        "19": {
 			"__type__": "Place",
            "conflictTiId": null,
            "maxSpeed": 0,
            "name": "LEFT",
            "nextTiId": null,
            "placeCode": "LFT",
            "previousTiId": null,
            "x": 20.0,
            "y": 10.0
        },
        "20": {
 			"__type__": "Place",
            "conflictTiId": null,
            "maxSpeed": 0,
            "name": "STATION",
            "nextTiId": null,
            "placeCode": "STN",
            "previousTiId": null,
            "x": 320.0,
            "y": 10.0
        },
        "21": {
 			"__type__": "Place",
            "conflictTiId": null,
            "maxSpeed": 0,
            "name": "RIGHT",
            "nextTiId": null,
            "placeCode": "RGT",
            "previousTiId": null,
            "x": 420.0,
            "y": 10.0
        },
        "22": {
            "__type__": "PlatformItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": null,
            "placeCode": "STN",
            "previousTiId": null,
            "trackCode": "2",
            "x": 300.0,
            "xf": 400.0,
            "y": 30.0,
            "yf": 45.0
        },
        "23": {
            "__type__": "PlatformItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": null,
            "placeCode": "STN",
            "previousTiId": null,
            "trackCode": "1",
            "x": 300.0,
            "xf": 400.0,
            "y": -10.0,
            "yf": -25.0
        },
		"24": {
            "__type__": "TextItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "2",
            "nextTiId": null,
            "previousTiId": null,
            "x": 345,
            "y": 50.0
        },
		"25": {
            "__type__": "TextItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": "1",
            "nextTiId": null,
            "previousTiId": null,
            "x": 345,
            "y": -50.0
        }
	},
	"signalLibrary": {
		"__type__": "SignalLibrary",
		"signalAspects": {
			"BUFFER": {
				"__type__": "SignalAspect",
				"lineStyle": 1,
				"outerShapes": [0, 0, 0, 0, 0, 0],
				"outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"shapes": [0, 0, 0, 0, 0, 0],
				"shapesColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"actions": [[1, 0]]
			},
			"UK_DANGER": {
				"__type__": "SignalAspect",
				"lineStyle": 0,
				"outerShapes": [0, 0, 0, 0, 0, 0],
				"outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"shapes": [1, 0, 0, 0, 0, 0],
				"shapesColors": ["#FF0000", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"actions": [[1, 0]]
			},
			"UK_CAUTION": {
				"__type__": "SignalAspect",
				"lineStyle": 0,
				"outerShapes": [0, 0, 0, 0, 0, 0],
				"outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"shapes": [1, 0, 0, 0, 0, 0],
				"shapesColors": ["#FFFF00", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"actions": [[2, 0]]
			},
			"UK_CLEAR": {
				"__type__": "SignalAspect",
				"lineStyle": 0,
				"outerShapes": [0, 0, 0, 0, 0, 0],
				"outerColors": ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"shapes": [1, 0, 0, 0, 0, 0],
				"shapesColors": ["#00FF00", "#000000", "#000000", "#000000", "#000000", "#000000"],
				"actions": [[0, 999]]
			}
		},
		"signalTypes": {
			"BUFFER": {
				"__type__": "SignalType",
				"states": [
					{
						"__type__": "SignalState",
						"aspectName": "BUFFER",
						"conditions": {}
					}
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
						"conditions": {}
					}
				]
			}

		}
	}
}`

