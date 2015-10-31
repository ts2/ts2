package ts2
import (
	"time"
	"encoding/json"
	"fmt"
)

type tuplet [3]int

type DelayGenerator struct {
	data []tuplet
}

func (dg *DelayGenerator) UnmarshalJSON(data []byte) error {
	var field []tuplet
	if err := json.Unmarshal(data, &field); err != nil {
		var single int
		if err := json.Unmarshal(data, &single); err != nil {
			return fmt.Errorf("Delay Generator: Unparsable JSON: %s", data)
		}
		dg.data = []tuplet{{single, single, 100}}
	} else {
		dg.data = field
	}
	return nil
}

type Time struct{time.Time}

func (h *Time) UnmarshalJSON(data []byte) error {
	var hourStr string
	if err := json.Unmarshal(data, &hourStr); err != nil {
		return fmt.Errorf("Times should be encoded as 00:00:00 strings in JSON, got %s instead", data)
	}
	t, err := time.Parse("15:04:05", hourStr)
	if err != nil {
		return fmt.Errorf("Invalid time %s", hourStr)
	}
	h.Time = t
	return nil
}
