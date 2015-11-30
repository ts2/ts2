package ts2

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

//func (pos *Position) UnmarshalJSON(data []byte) error {
//	type auxPos [3]float64
//
//	var rawPos auxPos
//	if err := json.Unmarshal(data, &rawPos); err != nil {
//		return fmt.Errorf("Unable to decode simulation JSON: %s", err)
//	}
//	pos.TrackItemId = int(rawPos[0])
//	pos.PreviousItemId = int(rawPos[1])
//	pos.PositionOnTI = rawPos[2]
//	return nil
//}

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

// IsOut returns true if this position is out of the scene, going forward
func (pos Position) IsOut() bool {
	if pos.TrackItem.Type() == "EndItem" && pos.PreviousItem != nil {
		return true
	}
	return false
}

// Next returns a position on the next TrackItem of this Position
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
NewPosition returns a pointer to a Position defined by the given Simulation pointer,
TrackItem Id, previous TrackItem Id and distance.
*/
func NewPosition(sim *Simulation, tiId int, ptiId int, distance float64) (*Position, error) {
	ti, ok := sim.TrackItems[tiId]
	if !ok {
		return nil, fmt.Errorf("Unknown item with ID: %i", tiId)
	}
	pti, ok := sim.TrackItems[ptiId]
	if !ok {
		return nil, fmt.Errorf("Unknown item with ID: %i", ptiId)
	}
	newPos := Position{ti, pti, distance}
	if !newPos.IsValid() {
		return nil, fmt.Errorf("Position (%i, %i, %f) is not valid", tiId, ptiId, distance)
	}
	return &newPos, nil
}
