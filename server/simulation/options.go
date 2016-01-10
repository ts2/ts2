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

type options struct {
	TrackCircuitBased       bool           `json:"trackCircuitBased"`
	ClientToken             string         `json:"clientToken"`
	CurrentScore            int            `json:"currentScore"`
	CurrentTime             Time           `json:"currentTime"`
	DefaultDelayAtEntry     DelayGenerator `json:"defaultDelayAtEntry"`
	DefaultMaxSpeed         float64        `json:"defaultMaxSpeed"`
	DefaultMinimumStopTime  DelayGenerator `json:"defaultMinimumStopTime"`
	DefaultSignalVisibility float64        `json:"defaultSignalVisibility"`
	Description             string         `json:"description"`
	ManagerToken            string         `json:"managerToken"`
	TimeFactor              int            `json:"timeFactor"`
	Title                   string         `json:"title"`
	Version                 string         `json:"version"`
	WarningSpeed            float64        `json:"warningSpeed"`
}
