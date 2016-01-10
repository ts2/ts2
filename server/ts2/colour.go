
package ts2

import (
	"encoding/json"
	"fmt"
	"time"
)



// A Colour stored as RGB values
type Color struct {
	R, G, B uint8
}

// Implement the Go color.Color interface.
func (col Color) RGBA() (r, g, b, a uint32) {
	r = uint32(col.R)
	g = uint32(col.G)
	b = uint32(col.B)
	a = 0xFFFF
	return
}

// Color.Hex() returns the hex "html" representation of the color, as in #ff0080.
func (col Color) Hex() string {
	return fmt.Sprintf("#%02x%02x%02x", uint8(col.R), uint8(col.G), uint8(col.B))
}

// FromHex() parses a "css/html" hex color-string, either in the 3 "#f0c" or 6 "#ff1034" digits form.
func FromHex(scol string) (Color, error) {
	format := "#%02x%02x%02x"

	var r, g, b uint8
	n, err := fmt.Sscanf(scol, format, &r, &g, &b)
	if err != nil {
		return Color{}, err
	}
	if n != 3 {
		return Color{}, fmt.Errorf("color: %v is not a hex-color", scol)
	}

	return Color{r, g, b}, nil
}



// UnmarshalJSON for the Color type
func (c *Color) UnmarshalJSON(data []byte) error {
	var rawString string
	if err := json.Unmarshal(data, &rawString); err != nil {
		return fmt.Errorf("Unable to read color string: %s (%s)", data, err)
	}
	col, err := FromHex(rawString)
	if err != nil {
		return fmt.Errorf("Unable to decode color: %s (%s)", data, err)
	}
	*c = col
	return nil
}
