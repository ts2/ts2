package ts2

/*
TrainType defines rolling stock type.
*/
type TrainType struct {
	Description  string   `json:"description"`
	EmergBraking float64  `json:"emergBraking"`
	Length       float64  `json:"length"`
	MaxSpeed     float64  `json:"maxSpeed"`
	StdAccel     float64  `json:"stdAccel"`
	StdBraking   float64  `json:"stdBraking"`
	ElementsStr  []string `json:"elements"`

	simulation *Simulation
}

// setSimulation sets the Simulation this TrainType is part of.
func (tt *TrainType) setSimulation(sim *Simulation) {
	tt.simulation = sim
}

// Elements returns the train types this TrainType is composed of.
func (tt *TrainType) Elements() []*TrainType {
	res := make([]*TrainType, 0)
	for _, code := range tt.ElementsStr {
		res = append(res, tt.simulation.TrainTypes[code])
	}
	return res
}
