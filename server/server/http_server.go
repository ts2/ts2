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
	"net/http"

	"github.com/ts2/ts2/server/simulation"
)

var sim *simulation.Simulation
var hub *Hub

/*
Run() - runs  StartHttpd() and StartWs() for the given simulation, at address and port.
*/
func Run(s *simulation.Simulation, addr, port string) {
	sim = s

	go StartHttpd(addr, port)

	hub = &Hub{}
	hub.run()
}



/*
StartHttpd-  starts the http server which currently serves on the following route paths: {WIP}

    / : Serves a HTTP home page with the server status and information about the loaded sim.
      It also includes a JavaScript WebSocket client to communicate and manage the server.

    /ws : WebSocket endpoint for all TS2 clients and managers.
*/
func StartHttpd(addr, port string) {
	// Set handlers
	http.HandleFunc("/", H_Home)
	http.HandleFunc("/ws", H_Websocket)

	serverAddress := fmt.Sprintf("%s:%s", addr, port)
	log.Printf("Starting HTTP at: http://%s\n", serverAddress)
	log.Fatal(http.ListenAndServe(serverAddress, nil))
}

