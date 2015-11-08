package ts2

import (
	"testing"
	"encoding/json"
	"time"
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
	}
}`

func TestLoadOptions(t *testing.T) {
	var sim Simulation
	if err := json.Unmarshal([]byte(simJson), &sim); err != nil {
		t.Errorf("Options: error while loading JSON: %s", err)
	}
	assertEqual(t, sim.Options.CurrentScore, 12, "Options/currentScore")
	sixOClock, _ := time.Parse("15:04:05", "06:00:00")
	assertEqual(t, sim.Options.CurrentTime, Time{sixOClock}, "Options/currentTime")
	assertTrue(t, sim.Options.DefaultDelayAtEntry.equals(DelayGenerator{[]tuplet{{0, 0, 100}}}), "Options/defaultDelayAtEntry")
	assertTrue(t, sim.Options.DefaultMinimumStopTime.equals(DelayGenerator{[]tuplet{{20, 40, 90}, {40, 120, 10}}}), "Options/defaultMinimumStopTime")
	assertEqual(t, sim.Options.DefaultMaxSpeed, 18.06, "Options/defaultMaxSpeed")
	assertEqual(t, sim.Options.DefaultSignalVisibility, 100.0, "Options/defaultSignalVisibility")
	assertEqual(t, sim.Options.Description, "This simulation is a demo sim !", "Options/description")
	assertEqual(t, sim.Options.Title, "Demo Sim", "Options/title")
	assertEqual(t, sim.Options.TimeFactor, 5, "Options/timeFactor")
	assertEqual(t, sim.Options.Version, "0.7", "Options/version")
	assertEqual(t, sim.Options.WarningSpeed, 8.34, "Options/warningSpeed")
	assertEqual(t, sim.Options.TrackCircuitBased, false, "Options/trackCircuitBased")
}

func TestLoadTrackItems(t *testing.T) {
	var sim Simulation
	if err := json.Unmarshal([]byte(simJson), &sim); err != nil {
		t.Errorf("TrackItems: error while loading JSON: %s", err)
	}
	assertEqual(t, len(sim.TrackItems), 9, "TrackItems: Not all loaded")

	li1, ok := sim.TrackItems[1].(LineItem)
	assertTrue(t, ok, "TrackItems: 1 not loaded")
	li3, ok := sim.TrackItems[3].(LineItem)
	assertTrue(t, ok, "TrackItems: 3 not loaded")
	ei4, ok := sim.TrackItems[4].(EndItem)
	assertTrue(t, ok, "TrackItems: 4 not loaded")
	ili5, ok := sim.TrackItems[5].(InvisibleLinkItem)
	assertTrue(t, ok, "TrackItems: 5 not loaded")
	pfi6, ok := sim.TrackItems[6].(PlatformItem)
	assertTrue(t, ok, "TrackItems: 6 not loaded")
	ti7, ok := sim.TrackItems[7].(TextItem)
	assertTrue(t, ok, "TrackItems: 7 not loaded")
	pi8, ok := sim.TrackItems[8].(PointsItem)
	assertTrue(t, ok, "TrackItems: 8 not loaded")
	li9, ok := sim.TrackItems[9].(LineItem)
	assertTrue(t, ok, "TrackItems: 9 not loaded")
	li10, ok := sim.TrackItems[10].(LineItem)
	assertTrue(t, ok, "TrackItems: 10 not loaded")

	assertEqual(t, li1.Name(), "", "TrackItems/Name")
	assertEqual(t, li1.NextItem(), li3, "TrackItems/NextItem")
	assertEqual(t, li1.PreviousItem(), ei4, "TrackItems/PreviousItem")
	assertEqual(t, li1.RealLength(), 40.0, "TrackItems/RealLength")
	assertEqual(t, li1.Origin(), Point{200.0, 100.0}, "TrackItems/Origin")
	assertEqual(t, li1.End(), Point{240.0, 100.0}, "TrackItems/End")
	assertEqual(t, li3.PreviousItem(), li1, "TrackItems/PreviousItem")
	assertEqual(t, li3.TrackCode(), "TC", "TrackItems/TrackCode")

	assertEqual(t, ei4.Origin(), li1.Origin(), "TrackItem/Link")

	assertEqual(t, ili5.MaxSpeed(), 35.0, "TrackItem/MaxSpeed")
	assertEqual(t, ili5.RealLength(), 45.0, "TrackItem/RealLength")
	assertEqual(t, ili5.Origin(), li3.End(), "TrackItem/Link")
	assertEqual(t, ili5.PreviousItem(), li3, "TrackItem/Link")
	assertEqual(t, ili5, li3.NextItem(), "TrackItem/Link")

	assertEqual(t, pfi6.Origin(), Point{10, 110}, "TrackItem/Origin")
	assertEqual(t, pfi6.End(), Point{129, 130}, "TrackItem/End")

	assertEqual(t, ti7.Name(), "Sample Text", "TrackItem/Name")
	assertEqual(t, ti7.Origin(), Point{-20, 615}, "TrackItem/End")

	assertEqual(t, pi8.Center(), Point{355, 150}, "PointsItems/Center")
	assertEqual(t, pi8.CommonEnd(), Point{-5, 0}, "PointsItem/CommonEnd")
	assertEqual(t, pi8.NormalEnd(), Point{5, 0}, "PointsItem/NormalEnd")
	assertEqual(t, pi8.ReverseEnd(), Point{5, 5}, "PointsItem/ReverseEnd")
	assertEqual(t, pi8.PreviousItem(), ili5, "PointsItem/Link")
	assertEqual(t, pi8.NextItem(), li9, "PointsItem/Link")
	assertEqual(t, pi8.ReverseItem(), li10, "PointsItem/Link")

	assertEqual(t, li9.PreviousItem(), pi8, "TrackItem/Link")
	assertEqual(t, li10.PreviousItem(), pi8, "TrackItem/Link")

	place, okBnk := sim.Places["BNK"]
	assertTrue(t, okBnk, "Places: BNK not loaded")
	assertEqual(t, place.Name(), "BANK", "Places/Name")
	assertEqual(t, li3.Place(), place, "TrackItems/Place")
	assertEqual(t, pfi6.Place(), place, "TrackItems/Place")
}
