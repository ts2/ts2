package ts2


type Train struct {
	appearTime     string
	initialDelay   string
	initialSpeed   float32
	nextPlaceIndex int
	serviceCode    string
	speed          float32
	status         int
	stoppedTime    int
	trainHead      Position
	trainId        int
	trainTypeCode  string
}