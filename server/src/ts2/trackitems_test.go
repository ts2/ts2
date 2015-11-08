package ts2

import (
	"testing"
	"encoding/json"
	"reflect"
)

func TestFollowingItem(t *testing.T) {
	var sim Simulation
	if err := json.Unmarshal([]byte(simJson), &sim); err != nil {
		t.Errorf("Options: error while loading JSON: %s", err)
	}
	li1, _ := sim.TrackItems[1].(LineItem)
	li3, _ := sim.TrackItems[3].(LineItem)
	ei4, _ := sim.TrackItems[4].(EndItem)
	ili5, _ := sim.TrackItems[5].(InvisibleLinkItem)
	fi1, _ := li1.FollowingItem(ei4, 0)
	fi1b, _ := li1.FollowingItem(li3, 0)
	fi3, _ := li3.FollowingItem(li1, 0)
	_, nle := li1.FollowingItem(ili5, 0)
	assertEqual(t, fi1, li3, "TrackItem/FollowingItem")
	assertEqual(t, fi1b, ei4, "TrackItem/FollowingItem")
	assertEqual(t, fi3, ili5, "TrackItem/FollowingItem")
	assertEqual(t, reflect.TypeOf(nle).Name(), "ItemsNotLinkedError", "TrackItem/FollowingItem")
}
