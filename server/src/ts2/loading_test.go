package ts2

import (
	"testing"
	"encoding/json"
	"time"
)

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

func TestLoadSignalLibrary(t *testing.T) {
	var sim Simulation
	if err := json.Unmarshal([]byte(simJson), &sim); err != nil {
		t.Errorf("SignalLibrary: error while loading JSON: %s", err)
	}
	assertEqual(t, len(sim.SignalLib.Types), 2, "SignalLibrary: Not all types loaded")
	assertEqual(t, len(sim.SignalLib.Aspects), 4, "SignalLibrary: Not all aspects loaded")
	bufferAspect, ok := sim.SignalLib.Aspects["BUFFER"]
	if !ok {
		t.Errorf("SignalLibrary: no BUFFER in aspects")
	}
	assertEqual(t, bufferAspect.LineStyle, BUFFER, "SignalLibrary/Aspects/LineStyle")
	assertEqual(t, bufferAspect.OuterShapes, [6]signalShape{NONE, NONE, NONE, NONE, NONE, NONE}, "SignalLibrary/Aspects/OuterShapes")
	black, _ := FromHex("#000000")
	assertEqual(t, bufferAspect.OuterColors, [6]Color{black, black, black, black, black, black}, "SignalLibrary/Aspects/OuterColors")
	assertEqual(t, bufferAspect.Shapes, [6]signalShape{NONE, NONE, NONE, NONE, NONE, NONE}, "SignalLibrary/Aspects/Shapes")
	assertEqual(t, bufferAspect.ShapesColors, [6]Color{black, black, black, black, black, black}, "SignalLibrary/Aspects/Colors")
	assertEqual(t, len(bufferAspect.Actions), 1, "SignalLibrary/Aspects: Not all actions loaded")
	assertEqual(t, bufferAspect.Actions[0].Target, BEFORE_THIS_SIGNAL, "SignalLibrary/Aspects/Actions/Target")
	assertEqual(t, bufferAspect.Actions[0].Speed, 0.0, "SignalLibrary/Aspects/Actions/Speed")
	dangerAspect, ok := sim.SignalLib.Aspects["UK_DANGER"]
	if !ok {
		t.Errorf("SignalLibrary: no UK_DANGER in aspects")
	}
	assertEqual(t, dangerAspect.LineStyle, LINE, "SignalLibrary/Aspects/LineStyle")
	assertEqual(t, dangerAspect.Shapes, [6]signalShape{CIRCLE, NONE, NONE, NONE, NONE, NONE}, "SignalLibrary/Aspects/Shapes")
	red, _ := FromHex("#FF0000")
	assertEqual(t, dangerAspect.ShapesColors, [6]Color{red, black, black, black, black, black}, "SignalLibrary/Aspects/Colors")
	cautionAspect, ok := sim.SignalLib.Aspects["UK_CAUTION"]
	if !ok {
		t.Errorf("SignalLibrary: no UK_CAUTION in aspects")
	}
	assertEqual(t, cautionAspect.Actions[0].Target, BEFORE_NEXT_SIGNAL, "SignalLibrary/Aspects/Actions/Target")
	assertEqual(t, cautionAspect.Actions[0].Speed, 0.0, "SignalLibrary/Aspects/Actions/Speed")
}
