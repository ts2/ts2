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
	"fmt"
)

/*
bigFloat is a large number used for the length of EndItem. It must be bigger
than the maximum distance the fastest train can travel during the game time step
at maximum simulation speed.
*/
const bigFloat = 1000000000.0

type CustomProperty map[string][]int

/*
An ItemsNotLinkedError is returned when two TrackItem instances that are assumed
to be linked; are not.
*/
type ItemsNotLinkedError struct {
	item1 TrackItem
	item2 TrackItem
}

func (e ItemsNotLinkedError) Error() string {
	return fmt.Sprintf("TrackItems %s and %s are not linked", e.item1, e.item2)
}

/*
A "TrackItem" is a piece of scenery and is "the base interface".

Every item has defined coordinates in the scenery layout and is connected to other
TrackItems's so that the trains can travel from one to another.

The coordinates are expressed in pixels, the X-axis is from left to right and
the Y-axis is from top to bottom.

Every TrackItem has an origin() Point defined by its X and Y values.
*/
type TrackItem interface {

	// TiId() returns the unique Id of this TrackItem, which is the index of this
	// item in the Simulation TrackItems map.
	TiId() int

	// Type() returns the name of the type of item this TrackItem is. This is
	// also the name of the interface that this type of item can implement.
	Type() string

	// Name() returns the human readable name of this item
	Name() string

	// setSimulation() attaches this TrackItem to a Simulation instance
	setSimulation(*Simulation)

	// setId() sets the item's internal id
	setId(int)

	// NextItem() returns the next item of this TrackItem.
	//
	// The next item is usually the item connected to the end of the item that is not the Origin()
	NextItem() TrackItem

	// PreviousItem returns the previous item of this TrackItem.
	//
	// The previous item is usually the item connected to the Origin() of this item.
	PreviousItem() TrackItem

	// MaxSpeed() is the maximum allowed speed on this TrackItem in meters per second.
	MaxSpeed() float64

	// RealLength() is the length in meters that this TrackItem has in real life track length
	RealLength() float64

	// Origin() are the two coordinates (x, y) of the origin point of this TrackItem.
	Origin() Point

	// Returns the conflicting item of this TrackItem. The conflicting
	// item is another item of the scenery on which a route must not be set if
	// one is already active on this TrackItem (and vice-versa). This is
	// particularly the case when two TrackItems cross over with no points.
	ConflictItem() TrackItem

	// Place returns the TrackItem of type Place associated with this item
	// (as defined by PlaceCode).
	Place() Place

	// FollowingItem returns the following TrackItem linked to this one,
	// knowing we come from precedingItem. Returned is either NextItem or
	// PreviousItem, depending which way we come from.
	//
	// The second argument will return a ItemsNotLinkedError if the given
	// precedingItem is not linked to this item.
	FollowingItem(TrackItem, Direction) (TrackItem, error)

	// IsConnected returns true if this TrackItem is connected to the given
	// TrackItem, false otherwise
	IsConnected(TrackItem) bool

	// CustomProperty returns the custom property with the given key
	CustomProperty(string) CustomProperty
}

/*
trackStruct is a struct the pointer of which implements TrackItem
*/
type trackStruct struct {
	TsName           string                    `json:"name"`
	NextTiId         int                       `json:"nextTiId"`
	PreviousTiId     int                       `json:"previousTiId"`
	TsMaxSpeed       float64                   `json:"maxSpeed"`
	TsRealLength     float64                   `json:"realLength"`
	X                float64                   `json:"x"`
	Y                float64                   `json:"y"`
	ConflictTiId     int                       `json:"conflictTiId"`
	CustomProperties map[string]CustomProperty `json:"customProperties"`
	PlaceCode        string                    `json:"placeCode"`

	tsId           int
	simulation     *Simulation
	activeRoute    *Route
	arPreviousItem TrackItem
	selected       bool
	trains         []*Train
}

func (ti *trackStruct) TiId() int {
	return ti.tsId
}

func (ti *trackStruct) Type() string {
	return "TrackItem"
}

func (ti *trackStruct) Name() string {
	return ti.TsName
}

func (ti *trackStruct) setSimulation(sim *Simulation) {
	ti.simulation = sim
}

func (ti *trackStruct) setId(tiId int) {
	ti.tsId = tiId
}

func (ti *trackStruct) NextItem() TrackItem {
	return ti.simulation.TrackItems[ti.NextTiId]
}

func (ti *trackStruct) PreviousItem() TrackItem {
	return ti.simulation.TrackItems[ti.PreviousTiId]
}

func (ti *trackStruct) MaxSpeed() float64 {
	if ti.TsMaxSpeed == 0 {
		return ti.simulation.Options.DefaultMaxSpeed
	}
	return ti.TsMaxSpeed
}

func (ti *trackStruct) RealLength() float64 {
	return ti.TsRealLength
}

func (ti *trackStruct) Origin() Point {
	return Point{ti.X, ti.Y}
}

func (ti *trackStruct) ConflictItem() TrackItem {
	return ti.simulation.TrackItems[ti.ConflictTiId]
}

func (ti *trackStruct) Place() Place {
	return ti.simulation.Places[ti.PlaceCode]
}

func (ti *trackStruct) FollowingItem(precedingItem TrackItem, dir Direction) (TrackItem, error) {
	if precedingItem == TrackItem(ti).PreviousItem() {
		return ti.NextItem(), nil
	}
	if precedingItem == TrackItem(ti).NextItem() {
		return ti.PreviousItem(), nil
	}
	return nil, ItemsNotLinkedError{ti, precedingItem}
}

func (ti *trackStruct) IsConnected(oti TrackItem) bool {
	if TrackItem(ti).NextItem() == oti || TrackItem(ti).PreviousItem() == ti {
		return true
	}
	return false
}

func (ti *trackStruct) CustomProperty(key string) CustomProperty {
	return ti.CustomProperties[key]
}

/*
ResizableItem is the base of any TrackItem that can be resized by the user in
the editor, such as LineItem or PlatformItem.
*/
type ResizableItem interface {
	TrackItem
	// End returns the two coordinates (Xf, Yf) of the end point of this
	// ResizeableItem.
	End() Point
}

/*
resizableStruct is a struct the pointer of which implements ResizableItem
*/
type resizableStruct struct {
	trackStruct
	Xf float64 `json:"xf"`
	Yf float64 `json:"yf"`
}

func (ri *resizableStruct) Type() string {
	return "ResizableItem"
}

func (ri *resizableStruct) End() Point {
	return Point{ri.Xf, ri.Yf}
}

/*
A Place is a special TrackItem representing a physical location such as a
station or a passing point. Place items are not linked to other items.
*/
type Place interface {
	TrackItem
}

/*
placeStruct is a struct the pointer of which implements Place
*/
type placeStruct struct {
	trackStruct
}

func (pl *placeStruct) Type() string {
	return "Place"
}

/*
A PlaceObject is an interface that TrackItem instances that interact with a
Place should implement.
*/
type PlaceObject interface {
	// TrackCode returns the track number of this LineItem, if it is part of a
	// place and if it has one.
	TrackCode() string
}

/*
A LineItem is a resizable TrackItem that represent a simple railway line and
that is used to connect two TrackItem together.
*/
type LineItem interface {
	ResizableItem
	PlaceObject
}

/*
lineStruct is a struct the pointer of which implements LineItem
*/
type lineStruct struct {
	resizableStruct
	TsTrackCode string `json:"trackCode"`
}

func (li *lineStruct) Type() string {
	return "LineItem"
}

func (li *lineStruct) TrackCode() string {
	return li.TsTrackCode
}

/*
InvisibleLinkItem behave like line items, but clients are encouraged not to
represented them on the scenery. They are used to make links between lines or to
represent bridges and tunnels.
*/
type InvisibleLinkItem interface {
	LineItem
}

/*
invisibleLinkStruct is a struct the pointer of which implements InvisibleLinkItem
*/
type invisibleLinkstruct struct {
	lineStruct
}

func (ili *invisibleLinkstruct) Type() string {
	return "InvisibleLinkItem"
}

/*
End items are invisible items to which the free ends of other Trackitem instances
must be connected to prevent the simulation from crashing.

End items are single point items.
*/
type EndItem interface {
	TrackItem
}

/*
endStruct is a struct the pointer of which implements EndItem
*/
type endStruct struct {
	trackStruct
}

func (ei *endStruct) Type() string {
	return "EndItem"
}

func (ei *endStruct) RealLength() float64 {
	return bigFloat
}

/*
Platform items are usually represented as a colored rectangle on the scene to
symbolise the platform. This colored rectangle can permit user interaction.
*/
type PlatformItem interface {
	ResizableItem
	PlaceObject
}

/*
platformStruct is a struct the pointer of which implements PlatformItem
*/
type platformStruct struct {
	lineStruct
}

func (pfi *platformStruct) Type() string {
	return "PlatformItem"
}

/*
TextItem is a prop to display simple text on the layout
*/
type TextItem interface {
	TrackItem
}

/*
textStruct is a struct the pointer of which implements TextItem
*/
type textStruct struct {
	trackStruct
}

func (ti *textStruct) Type() string {
	return "TextItem"
}

/*
PointsItem is a three-way junction.

The three ends are called `common end`, `normal end` and `reverse end`

	                    ____________ reverse
	                   /
	common ___________/______________normal

Trains can go from common end to normal or reverse ends depending on the
state of the points, but they cannot go from normal end to reverse end.
Usually, the normal end is aligned with the common end and the reverse end
is sideways, but this is not mandatory.

Points are represented on a 10 x 10 square centered on Center point. CommonEnd,
NormalEnd and ReverseEnd are points on the side of this square (i.e. they have
at least one coordinate which is 5 or -5)
*/
type PointsItem interface {
	TrackItem
	// The center point of this PointsItem in the scene coordinates
	Center() Point
	// CommonEnd return the common end point in the item's coordinates
	CommonEnd() Point
	// NormalEnd return the normal end point in the item's coordinates
	NormalEnd() Point
	// ReverseEnd return the reverse end point in the item's coordinates
	ReverseEnd() Point
	// ReversedItem returns the item linked to the reverse end of these points
	ReverseItem() TrackItem
	// Reversed returns true if the points are in the reversed position, false
	// otherwise
	Reversed() bool
}

/*
pointsStruct is a struct the pointer of which implements PointsItem
*/
type pointsStruct struct {
	trackStruct
	Xc          float64 `json:"xf"`
	Yc          float64 `json:"yf"`
	Xn          float64 `json:"xn"`
	Yn          float64 `json:"yn"`
	Xr          float64 `json:"xr"`
	Yr          float64 `json:"yr"`
	ReverseTiId int     `json:"reverseTiId"`
	reversed    bool
}

func (pi *pointsStruct) Type() string {
	return "PointsItem"
}

func (pi *pointsStruct) Center() Point {
	return Point{pi.X, pi.Y}
}

func (pi *pointsStruct) CommonEnd() Point {
	return Point{pi.Xc, pi.Yc}
}

func (pi *pointsStruct) NormalEnd() Point {
	return Point{pi.Xn, pi.Yn}
}

func (pi *pointsStruct) ReverseEnd() Point {
	return Point{pi.Xr, pi.Yr}
}

func (pi *pointsStruct) ReverseItem() TrackItem {
	return pi.simulation.TrackItems[pi.ReverseTiId]
}

func (pi *pointsStruct) Reversed() bool {
	return pi.reversed
}
func (ti *pointsStruct) FollowingItem(precedingItem TrackItem, dir Direction) (TrackItem, error) {
	if precedingItem == PointsItem(ti).ReverseItem() || precedingItem == PointsItem(ti).NextItem() {
		return ti.PreviousItem(), nil
	}
	if precedingItem == PointsItem(ti).PreviousItem() {
		if dir == REVERSED {
			return ti.ReverseItem(), nil
		} else {
			return ti.NextItem(), nil
		}
	}
	return nil, ItemsNotLinkedError{ti, precedingItem}
}
