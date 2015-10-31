package ts2

import "time"

type ServiceLine struct {
	mustStop               int
	placeCode              string
	scheduledArrivalTime   time.Time
	scheduledDepartureTime time.Time
	trackCode              string
}

type Service struct {
	autoReverse      bool
	description      string
	lines            []ServiceLine
	nextServiceCode  string
	plannedTrainType string
	serviceCode      string
}