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
	//	"encoding/json"
	"fmt"
)

/*
A Position object is a point on a TrackItem.

A Position is defined as being positionOnTI meters away from the end of this
TrackItem that is connected to PreviousItem.

Note that a Position has a direction, so that for any point on a TrackItem,
there are two Positions that can be defined:

- one starting from one end of the TrackItem.
- the other starting from the other end.

You can get the other Position by calling Reversed()
*/
type Position struct {
	TrackItem    TrackItem
	PreviousItem TrackItem
	PositionOnTI float64
}

/*
IsValid returns true if this is a valid position (i.e. items are connected, and
distance is positive), false otherwise.
*/
func (pos Position) IsValid() bool {
	if !pos.TrackItem.IsConnected(pos.PreviousItem) {
		return true
	}
	return false
}

// IsOut() is true if this position is out of the scene and moving forward
func (pos Position) IsOut() bool {
	if pos.TrackItem.Type() == "EndItem" && pos.PreviousItem != nil {
		return true
	}
	return false
}

// Position.Next() is the Position on the next TrackItem with regard to this Position
func (pos Position) Next(dir Direction) Position {
	nextTi, _ := pos.TrackItem.FollowingItem(pos.PreviousItem, dir)
	return Position{nextTi, pos.TrackItem, 0}
}

/*
Reversed returns the position that is at the same position but in the
opposite direction.
*/
func (pos Position) Reversed() Position {
	ti := pos.TrackItem
	pti := pos.PreviousItem
	nti, _ := ti.FollowingItem(pti, 0)
	distance := pos.TrackItem.RealLength() - pos.PositionOnTI
	return Position{ti, nti, distance}
}

/*
NewPosition returns a pointer to a Position defined by the given Simulation
pointer and PositionRepr.
*/
func NewPosition(sim *Simulation, posRepr PositionRepr) (*Position, error) {
	ti, ok := sim.TrackItems[posRepr.TrackItemId]
	if !ok {
		return nil, fmt.Errorf("Unknown item with ID: %i", posRepr.TrackItemId)
	}
	pti, ok := sim.TrackItems[posRepr.PreviousItemId]
	if !ok {
		return nil, fmt.Errorf("Unknown item with ID: %i", posRepr.PreviousItemId)
	}
	newPos := Position{ti, pti, posRepr.PositionOnTi}
	if !newPos.IsValid() {
		return nil, fmt.Errorf("Position (%i, %i, %f) is not valid", posRepr.TrackItemId, posRepr.PreviousItemId, posRepr.PositionOnTi)
	}
	return &newPos, nil
}

/*
PositionRepr is a representation of a Position that is independant of a Simulation
Object.
*/
type PositionRepr struct {
	TrackItemId    int     `json:"trackItem"`
	PreviousItemId int     `json:"previousTI"`
	PositionOnTi   float64 `json:"positionOnTI"`
}
