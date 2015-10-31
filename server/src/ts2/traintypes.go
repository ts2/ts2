package ts2


type TrainType struct {
	code         string
	description  string
	emergBraking float32
	length       float32
	maxSpeed     float32
	stdAccel     float32
	stdBraking   float32
	elements	 []string
}