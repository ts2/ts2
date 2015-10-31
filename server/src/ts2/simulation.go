package ts2

type Simulation struct {
	TrackItems []*TrackItem `json:"trackItems"`
	Options    options      `json:"options"`
}

var Sim *Simulation