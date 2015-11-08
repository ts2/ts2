package ts2
import (
	"encoding/json"
	"fmt"
	"strings"
	"strconv"
)

type Simulation struct {
	TrackItems map[int]TrackItem
	Places     map[string]Place
	Options    options
}

func (sim *Simulation) UnmarshalJSON(data []byte) error {
	type auxItem map[string]json.RawMessage

	type auxSim struct {
		TrackItems map[string]json.RawMessage
		Options    options
	}

	var rawSim auxSim
	if err := json.Unmarshal(data, &rawSim); err != nil {
		return fmt.Errorf("Unable to decode simulation JSON: %s", err)
	}
	sim.TrackItems = make(map[int]TrackItem)
	sim.Places = make(map[string]Place)
	for tiId, tiString := range rawSim.TrackItems {
		var rawItem auxItem
		if err := json.Unmarshal(tiString, &rawItem); err != nil {
			return fmt.Errorf("Unable to read TrackItem: %s. %s", tiString, err)
		}

		tiType := string(rawItem["__type__"])
		unmarshalItem := func(ti TrackItem) error {
			if err := json.Unmarshal(tiString, ti); err != nil {
				return fmt.Errorf("Unable to decode %s: %s. %s", tiType, tiString, err)
			}
			tiId, _ := strconv.Atoi(strings.Trim(tiId, `"`))
			Sim.TrackItems[tiId] = ti
			return nil
		}

		switch tiType {
		case `"LineItem"`:
			var ti lineStruct
			unmarshalItem(&ti)
		case `"InvisibleLinkItem"`:
			var ti invisibleLinkstruct
			unmarshalItem(&ti)
		case `"EndItem"`:
			var ti endStruct
			unmarshalItem(&ti)
		case `"PlatformItem"`:
			var ti platformStruct
			unmarshalItem(&ti)
		case `"TextItem"`:
			var ti textStruct
			unmarshalItem(&ti)
		case `"PointsItem"`:
			var ti pointsStruct
			unmarshalItem(&ti)
		case `"Place"`:
			var pl placeStruct
			if err := json.Unmarshal(tiString, &pl); err != nil {
				return fmt.Errorf("Unable to decode Place: %s. %s", tiString, err)
			}
			sim.Places[pl.PlaceCode] = Place(&pl)
		default:
			return fmt.Errorf("Unknown TrackItem type: %s", rawItem["__type__"])
		}

	}
	sim.Options = rawSim.Options
	return nil
}

var Sim *Simulation
