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

/*
TrainType defines a rolling stock type.
*/
type TrainType struct {
	Description  string   `json:"description"`
	EmergBraking float64  `json:"emergBraking"`
	Length       float64  `json:"length"`
	MaxSpeed     float64  `json:"maxSpeed"`
	StdAccel     float64  `json:"stdAccel"`
	StdBraking   float64  `json:"stdBraking"`
	ElementsStr  []string `json:"elements"`

	simulation *Simulation
}

// setSimulation() attaches the simulation this TrainType is part of
func (tt *TrainType) setSimulation(sim *Simulation) {
	tt.simulation = sim
}

// Elements() returns the train types this TrainType is composed of.
func (tt *TrainType) Elements() []*TrainType {
	res := make([]*TrainType, 0)
	for _, code := range tt.ElementsStr {
		res = append(res, tt.simulation.TrainTypes[code])
	}
	return res
}
