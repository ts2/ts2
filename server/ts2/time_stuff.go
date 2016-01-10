
package ts2

import (
	"encoding/json"
	"fmt"
	"time"
)

type tuplet [3]int

/*
DelayGenerator is a probability distribution for a duration in seconds.

It is used to have random delays of trains.

The `data` field is a list of tuplets and an array of 3 integers.

Each tuple defines in order:
- A lower bound
- An upper bound
- A probability in percent of the value to be inside the defined bounds.

e.g. [[0 100 80] [100 500 20]] means that when a value will be yielded by
this DelayGenerator, it will have 80% chance of being between 0 and 100, and
20% chance of being between 100 and 500.
*/
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

/*
Time type for the simulation (HH:MM:SS).

Valid Time objects start on 0000-01-02.
*/
type Time struct{ time.Time }

func (h *Time) UnmarshalJSON(data []byte) error {
	var hourStr string
	if err := json.Unmarshal(data, &hourStr); err != nil {
		return fmt.Errorf("Times should be encoded as 00:00:00 strings in JSON, got %s instead", data)
	}
	*h = ParseTime(hourStr)
	return nil
}

/*
ParseTime returns a Time object from its string representation in format 15:04:05
*/
func ParseTime(data string) Time {
	t, err := time.Parse("15:04:05", data)
	if err != nil {
		return Time{}
	}
	// We add 24 hours to make a difference between 00:00:00 and an empty Time
	return Time{t.Add(24 * time.Hour)}
}