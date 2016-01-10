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

package server

import (
	"fmt"
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
	readChan chan *connection
	// Objects received from simulation
	writeChan chan interface{}
}

/*
Hub.run() is the loop for handling dispatching requests and responses
*/
func (h *Hub) run() {
	log.Print("Hub: starting...")
	// make connection maps
	h.clientConnections = make(map[*connection]bool)
	h.managerConnections = make(map[*connection]bool)
	// make channels
	h.registerChan = make(chan *connection)
	h.unregisterChan = make(chan *connection)
	h.readChan = make(chan *connection)
	h.writeChan = make(chan interface{}, 256)
	for {
		select {
		case o := <-h.writeChan:
			log.Printf("Object to write: %s", o)
		case c := <-h.readChan:
			go h.dispatchObject(c.LastRequest, c.pushChan)
		case c := <-h.registerChan:
			h.register(c)
		case c := <-h.unregisterChan:
			h.unregister(c)
		}
	}
}

/*
Hub.register() registers the connection to this hub
*/
func (h *Hub) register(c *connection) {
	switch c.clientType {
	case CLIENT:
		h.clientConnections[c] = true
	case MANAGER:
		h.managerConnections[c] = true
	}
}

/*
Hub.unregister() unregisters the connection to this hub
*/
func (h *Hub) unregister(c *connection) {
	switch c.clientType {
	case CLIENT:
		if _, ok := h.clientConnections[c]; ok {
			delete(h.clientConnections, c)
		}
	case MANAGER:
		if _, ok := h.managerConnections[c]; ok {
			delete(h.managerConnections, c)
		}
	}
}

/*
dispatchObject process a request and
*/
func (h *Hub) dispatchObject(req Request, ch chan interface{}) {
	switch req.Object {
	case "Server":
		h.dispatchServer(req, ch)
		//	case "Simulation":
		//		h.dispatchSimulation(req, ch)
		//	case "TrackItem":
		//		h.dispatchTrackItem(req, ch)
		//	case "Route":
		//		h.dispatchRoute(req, ch)
		//	case "TrainType":
		//		h.dispatchTrainType(req, ch)
		//	case "Service":
		//		h.dispatchService(req, ch)
		//	case "Train":
		//		h.dispatchTrain(req, ch)
	}
}

/*
dispatchServer processes requests made on the Server object
*/
func (h *Hub) dispatchServer(req Request, ch chan interface{}) {
	switch req.Action {
	case "login":
		ch <- NewErrorResponse(fmt.Errorf("Can't call login when already logged in"))
	}
}
