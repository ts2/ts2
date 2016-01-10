/*   Copyright (C) 2008-2016 by Nicolas Piganeau and the TS2 team
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

type MessageType uint8

const (
	SOFTWARE_MSG       MessageType = 0
	PLAYER_WARNING_MSG MessageType = 1
	SIMULATION_MSG     MessageType = 2
)

/*
Message is one message emitted to the Message Logger of the simulation.
*/
type Message struct {
	MsgType MessageType `json:"msgType"`
	MsgText string      `json:"msgText"`
}

/*
MessageLogger holds all Message instances that have been emitted to it.
*/
type MessageLogger struct {
	Messages []Message `json:"messages"`

	simulation *Simulation
}

/*
setSimulation sets the Simulation this MessageLogger is part of.
*/
func (ml *MessageLogger) setSimulation(sim *Simulation) {
	ml.simulation = sim
}
