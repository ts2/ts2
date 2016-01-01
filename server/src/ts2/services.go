package ts2

type ServiceActionCode int

const (
	// Reverse the train
	ACTION_REVERSE ServiceActionCode = 1
	// Set the given service. ActionParam is the new service code
	ACTION_SET_SERVICE ServiceActionCode = 2
	// Split the train at the given position. ActionParam is the element after
	// which to split (integer).
	ACTION_SPLIT ServiceActionCode = 3
	// Join the train. ActionParam is 'ahead' if to join with the train in
	// front or 'behind' otherwise.
	ACTION_JOIN ServiceActionCode = 4
)

type ServiceAction struct {
	ActionCode  ServiceActionCode `json:"actionCode"`
	ActionParam string            `json:"actionParam"`
}

/*
ServiceLine is a line of the definition of the Service.
It consists of a place (usually a station) with a track number
and scheduled times to arrive at and depart from this station.
*/
type ServiceLine struct {
	MustStop               bool   `json:"mustStop"`
	PlaceCode              string `json:"placeCode"`
	ScheduledArrivalTime   Time   `json:"scheduledArrivalTime"`
	ScheduledDepartureTime Time   `json:"scheduledDepartureTime"`
	TrackCode              string `json:"TrackCode"`

	service *Service
}

/*
Place returns the place interface associated with this service line
*/
func (sl *ServiceLine) Place() Place {
	return sl.service.simulation.Places[sl.PlaceCode]
}

/*
A Service is mainly a predefined schedule that trains are supposed to
follow with a few additional informations.
The schedule is composed of several "lines" of type ServiceLine
*/
type Service struct {
	Description          string           `json:"description"`
	Lines                []*ServiceLine   `json:"lines"`
	PlannedTrainTypeCode string           `json:"plannedTrainType"`
	PostActions          []*ServiceAction `json:"postActions"`

	simulation *Simulation
}

/*
PlannedTrainType returns a pointer to the planned TrainType for this Service.
*/
func (s *Service) PlannedTrainType() *TrainType {
	return s.simulation.TrainTypes[s.PlannedTrainTypeCode]
}

/*
setSimulation sets the Simulation this Service is part of.
*/
func (s *Service) setSimulation(sim *Simulation) {
	s.simulation = sim
	for _, line := range s.Lines {
		line.service = s
	}
}
