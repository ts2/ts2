package ts2

type customProperty map[string][]int

type TrackItem struct {
	TiId int
	TiType string `json:"__type__"`
	Name string
	NextTiId int
	PreviousTiId int
	reverseTiId int
	conflictTiId int
	maxSpeed float32
	realLength float32
	reverse int
	customProperties map[string]customProperty
	signalType string
	placeCode string
	trackCode string
	x float32
	y float32
	xn float32
	yn float32
	xf float32
	yf float32
	xr float32
	yr float32
}

func (ti *TrackItem) NextItem() *TrackItem {
	return Sim.TrackItems[ti.nextTiId]
}
