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
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 0.0,
            "name": null,
            "nextTiId": 3,
            "placeCode": null,
            "previousTiId": 4,
            "realLength": 40.0,
            "trackCode": "",
            "x": 200.0,
            "xf": 240.0,
            "y": 100.0,
            "yf": 100.0
        },
        "3": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 123.0,
            "name": "Sample Name",
            "nextTiId": 5,
            "placeCode": "BNK",
            "previousTiId": 1,
            "realLength": 40.0,
            "trackCode": "TC",
            "x": 240.0,
            "xf": 290.0,
            "y": 100.0,
            "yf": 150.0
        },
        "4":{
            "__type__": "EndItem",
            "conflictTiId": null,
            "maxSpeed": 18.06,
            "name": null,
            "nextTiId": null,
            "previousTiId": 1,
            "x": 200.0,
            "y": 100.0
        },
        "5": {
            "__type__": "InvisibleLinkItem",
            "conflictTiId": null,
            "maxSpeed": 35.0,
            "name": null,
            "nextTiId": 8,
            "placeCode": null,
            "previousTiId": 3,
            "realLength": 45.0,
            "trackCode": null,
            "x": 290.0,
            "xf": 350.0,
            "y": 150.0,
            "yf": 150.0
        },
        "100": {
 			"__type__": "Place",
            "conflictTiId": null,
            "maxSpeed": 0,
            "name": "BANK",
            "nextTiId": null,
            "placeCode": "BNK",
            "previousTiId": null,
            "tiId": 100,
            "x": 60.0,
            "y": 50.0
        },
        "6": {
            "__type__": "PlatformItem",
            "conflictTiId": null,
            "maxSpeed": 18.06,
            "name": null,
            "nextTiId": null,
            "placeCode": "BNK",
            "previousTiId": null,
            "trackCode": "7",
            "x": 10.0,
            "xf": 129.0,
            "y": 110.0,
            "yf": 130.0
        },
		"7": {
            "__type__": "TextItem",
            "conflictTiId": null,
            "maxSpeed": 6.7,
            "name": "Sample Text",
            "nextTiId": null,
            "previousTiId": null,
            "x": -20.0,
            "y": 615.0
        },
        "8": {
            "__type__": "PointsItem",
            "conflictTiId": null,
            "maxSpeed": 18.06,
            "name": null,
            "nextTiId": 9,
            "previousTiId": 5,
            "reverseTiId": 10,
            "x": 355.0,
            "xf": -5.0,
            "xn": 5.0,
            "xr": 5.0,
            "y": 150.0,
            "yf": 0.0,
            "yn": 0.0,
            "yr": 5.0
		},
        "9": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 123.0,
            "name": null,
            "nextTiId": 522,
            "placeCode": null,
            "previousTiId": 8,
            "realLength": 40.0,
            "trackCode": null,
            "x": 360.0,
            "xf": 400.0,
            "y": 150.0,
            "yf": 150.0
        },
        "10": {
            "__type__": "LineItem",
            "conflictTiId": null,
            "maxSpeed": 123.0,
            "name": null,
            "nextTiId": 523,
            "placeCode": null,
            "previousTiId": 8,
            "realLength": 40.0,
            "trackCode": null,
            "x": 360.0,
            "xf": 400.0,
            "y": 155.0,
            "yf": 195.0
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

