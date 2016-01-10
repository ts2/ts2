/*   Copyright (C) 2008-2016 by Nicolas Piganeau and the TS2 TEAM
 *   (See AUTHORS file)
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package simulation

import (
	"encoding/json"
	"fmt"
	"time"
)

/*
DelayGenerator is a probability distribution for a duration in seconds; atmo

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
type delayTuplet [3]int

type DelayGenerator struct {
	data []delayTuplet
}

func (dg *DelayGenerator) UnmarshalJSON(data []byte) error {
	var field []delayTuplet
	if err := json.Unmarshal(data, &field); err != nil {
		var single int
		if err := json.Unmarshal(data, &single); err != nil {
			return fmt.Errorf("Delay Generator: Unparsable JSON: %s", data)
		}
		dg.data = []delayTuplet{{single, single, 100}}
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
