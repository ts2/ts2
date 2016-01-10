
package ts2

type TrainStatus uint8

const (
	//	Not yet entered on the scene
	INACTIVE TrainStatus = 0

	// Running with a positive speed
	RUNNING TrainStatus = 10

	// Scheduled stop, e.g. at a station
	STOPPED TrainStatus = 20

	// Unscheduled stop, e.g. at a red signal
	WAITING TrainStatus = 30

	// Exited the area
	OUT TrainStatus = 40

	// Ended its service and no new service assigned
	END_OF_SERVICE TrainStatus = 50
)

/*
Train is a stock of `TrainType` running on a track at a certain speed and to which
is assigned a Service.
*/
type Train struct {
	AppearTime     Time           `json:"appearTime"`
	InitialDelay   DelayGenerator `json:"initialDelay"`
	InitialSpeed   float64        `json:"initialSpeed"`
	NextPlaceIndex int            `json:"nextPlaceIndex"`
	ServiceCode    string         `json:"serviceCode"`
	Speed          float64        `json:"speed"`
	Status         TrainStatus    `json:"status"`
	StoppedTime    int            `json:"stoppedTime"`
	TrainHeadRepr  PositionRepr   `json:"trainHead"`
	TrainTypeCode  string         `json:"trainTypeCode"`
	TrainHead      *Position

	simulation *Simulation
}

/*
setSimulation() attaches the Simulation to this Tra, and in is part of and initialized TrainHead.
*/
func (t *Train) setSimulation(sim *Simulation) {
	t.simulation = sim
	if th, err := NewPosition(sim, t.TrainHeadRepr); err != nil {
		panic(err)
	} else {
		t.TrainHead = th
	}
}

/*
Train.Service() returns a pointer to the Service assigned to this Train, or nil if no
Service is assigned.
*/
func (t *Train) Service() *Service {
	return t.simulation.Services[t.ServiceCode]
}

/*
Train.TrainType() returns a pointer to the TrainType of this Train and running.
*/
func (t *Train) TrainType() *TrainType {
    // ummm said pedro
	return t.simulation.TrainTypes[t.TrainTypeCode]
}
