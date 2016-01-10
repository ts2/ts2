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
	"reflect"
	"testing"
)

func TestFollowingItem(t *testing.T) {
	var sim Simulation
	if err := json.Unmarshal(loadSim(), &sim); err != nil {
		t.Errorf("Options: error while loading JSON: %s", err)
	}
	ei1, _ := sim.TrackItems[1]
	li2, _ := sim.TrackItems[2]
	si3, _ := sim.TrackItems[3]
	li4, _ := sim.TrackItems[4]
	ti6, _ := sim.TrackItems[6]
	pi7, _ := sim.TrackItems[7]
	ti8, _ := sim.TrackItems[8]
	ti14, _ := sim.TrackItems[14]
	fi1, _ := li2.FollowingItem(si3, 0)
	fi1b, _ := li2.FollowingItem(ei1, 0)
	fi3, _ := si3.FollowingItem(li4, 1)
	_, nle := ei1.FollowingItem(si3, 0)
	fipr, _ := pi7.FollowingItem(ti6, 1)
	fipn, _ := pi7.FollowingItem(ti6, 0)
	ficr, _ := pi7.FollowingItem(ti14, 0)
	ficrb, _ := pi7.FollowingItem(ti14, 1)
	ficn, _ := pi7.FollowingItem(ti8, 0)
	assertEqual(t, fi1, ei1, "TrackItem/FollowingItem")
	assertEqual(t, fi1b, si3, "TrackItem/FollowingItem")
	assertEqual(t, fi3, li2, "TrackItem/FollowingItem")
	assertEqual(t, reflect.TypeOf(nle).Name(), "ItemsNotLinkedError", "TrackItem/FollowingItem")
	assertEqual(t, fipr, ti14, "PointsItem/FollowingItem")
	assertEqual(t, fipn, ti8, "PointsItem/FollowingItem")
	assertEqual(t, ficr, ti6, "PointsItem/FollowingItem")
	assertEqual(t, ficrb, ti6, "PointsItem/FollowingItem")
	assertEqual(t, ficn, ti6, "PointsItem/FollowingItem")
}
