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

package main

import (
	"log"
)

/*
Hub makes the interface between the Simulation and the websocket clients
*/
type Hub struct {
	// Registered client connections
	clientConnections map[*connection]bool

	// Registered train manager connections
	managerConnections map[*connection]bool

	// Register requests from the connection
	registerChan chan *connection

	// Unregister requests from connection
	unregisterChan chan *connection

	// Received requests channel
	readChan chan *Request
}

/*
Hub.run() is the loop for handling dispatching requests and responses
*/
func (h *Hub) run() {
	log.Print("Hub: starting...")
	h.registerChan = make(chan *connection)
	h.unregisterChan = make(chan *connection)
	h.readChan = make(chan *Request)
	for {
		select {
		case c := <-h.registerChan:
			h.register(c)
			log.Printf("Hub: registering connection from %s", c.RemoteAddr())
		case c := <-h.unregisterChan:
			h.unregister(c)
		case req := <-h.readChan:
			log.Printf("REQ: %s", req)
		}
	}
}

/*
Hub.register() registers the connection to this hub
*/
func (h *Hub) register(c *connection) error {
	return nil
}

/*
Hub.unregister() unregisters the connection to this hub
*/
func (h *Hub) unregister(c *connection) error {
	return nil
}
