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
	"strconv"
)

// RouteState represents the state of a Route at a given time and instance
type RouteState uint8

const (
	// DEACTIVATED =  The route is not active
	DEACTIVATED RouteState = 0

	// ACTIVATED =  The route is active but will be destroyed by the first train using it
	ACTIVATED RouteState = 1

	// PERSISTENT =  The route is set and will remain after train passage
	PERSISTENT RouteState = 2
)

// Direction are constants that represent the "state" of a points, either normal or reversed
type Direction uint8

const (
	// Rail change set at normal
	NORMAL Direction = 0

	// Rail change is set for cross over
	REVERSED Direction = 1

	// Point is moving and Unknown state
	MOVING Direction = 10

	// Point goes back to previous safe state.. and fail
	BACKOFF Direction = 11
)

/*
Route is a path between two signals.

If a route is activated, the path is selected, and the signals at the beginning
and the end of the route are changed and the conflicting possible other routes
are inhibited. Routes are static and defined in the game file. The player can
only activate or deactivate them.
*/
type Route struct {
	simulation    *Simulation
	BeginSignalId int
	EndSignalId   int
	InitialState  RouteState
	Directions    map[int]Direction

	State     RouteState
	positions []Position
}

// BeginSignal returns the SignalItem at which this Route starts.
func (r *Route) BeginSignal() SignalItem {
	return r.simulation.TrackItems[r.BeginSignalId].(SignalItem)
}

// EndSignal returns the SignalItem at which this Route ends.
func (r *Route) EndSignal() SignalItem {
	return r.simulation.TrackItems[r.EndSignalId].(SignalItem)
}

// setSimulation sets the Simulation this Route is part of.
func (r *Route) setSimulation(sim *Simulation) {
	r.simulation = sim
}

// initialize does initial steps necessary to use this route
func (r *Route) initialize() error {
	// Initialize state to initial state
	r.State = r.InitialState
	// Populate positions slice
	pos := Position{r.BeginSignal(), r.BeginSignal().PreviousItem(), 0}
	for !pos.IsOut() {
		r.positions = append(r.positions, pos)
		if pos.TrackItem == r.EndSignal() {
			return nil
		}
		dir, ok := r.Directions[pos.TrackItem.TiId()]
		if !ok {
			dir = Direction(0)
		}
		pos = pos.Next(dir)
	}
	return fmt.Errorf("Unable to link signal %i to signal %i", r.BeginSignalId, r.EndSignalId)
}

func (r *Route) UnmarshalJSON(data []byte) error {
	type auxRoute struct {
		BeginSignalId int                  `json:"beginSignal"`
		EndSignalId   int                  `json:"endSignal"`
		InitialState  RouteState           `json:"initialState"`
		Directions    map[string]Direction `json:"directions"`
	}
	var rawRoute auxRoute
	if err := json.Unmarshal(data, &rawRoute); err != nil {
		return fmt.Errorf("Unable to decode simulation JSON: %s", err)
	}
	r.BeginSignalId = rawRoute.BeginSignalId
	r.EndSignalId = rawRoute.EndSignalId
	r.InitialState = rawRoute.InitialState
	r.Directions = make(map[int]Direction)
	for tiIdStr, dir := range rawRoute.Directions {
		tiId, _ := strconv.Atoi(tiIdStr)
		r.Directions[tiId] = dir
	}
	return nil
}
