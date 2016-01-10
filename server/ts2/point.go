
package ts2

import (
	"encoding/json"
	"fmt"
	"time"
)



/*
Point type represents a point on the scenery
*/
type Point struct {
	X float64
	Y float64
}

func Add(p1 Point, p2 Point) Point {
	return Point{p1.X + p2.X, p1.Y + p2.Y}
}


