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
