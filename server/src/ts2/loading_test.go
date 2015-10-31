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
	}
}`

func TestLoadOptions(t *testing.T) {
	var sim Simulation
	if err := json.Unmarshal([]byte(simJson), &sim); err != nil{
		t.Errorf("Options: error while loading JSON: %s", err)
	}
	assertEqual(t, sim.Options.CurrentScore, 12, "Options/currentScore")
	sixOClock, _ := time.Parse("15:04:05", "06:00:00")
	assertEqual(t, sim.Options.CurrentTime, Time{sixOClock}, "Options/currentTime")
	assertTrue(t, sim.Options.DefaultDelayAtEntry.equals(DelayGenerator{[]tuplet{{0, 0, 100}}}), "Options/defaultDelayAtEntry")
	assertTrue(t, sim.Options.DefaultMinimumStopTime.equals(DelayGenerator{[]tuplet{{20, 40, 90}, {40, 120, 10}}}), "Options/defaultMinimumStopTime")
	assertEqual(t, sim.Options.DefaultMaxSpeed, float32(18.06), "Options/defaultMaxSpeed")
	assertEqual(t, sim.Options.DefaultSignalVisibility, float32(100), "Options/defaultSignalVisibility")
	assertEqual(t, sim.Options.Description, "This simulation is a demo sim !", "Options/description")
	assertEqual(t, sim.Options.Title, "Demo Sim", "Options/title")
	assertEqual(t, sim.Options.TimeFactor, 5, "Options/timeFactor")
	assertEqual(t, sim.Options.Version, "0.7", "Options/version")
	assertEqual(t, sim.Options.WarningSpeed, float32(8.34), "Options/warningSpeed")
	assertEqual(t, sim.Options.TrackCircuitBased, false, "Options/trackCircuitBased")
}


