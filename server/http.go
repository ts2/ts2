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
	"fmt"
	"html/template"
	"log"
	"net/http"
)

var homeTempl = template.Must(template.ParseFiles("home.html"))

/*
HttpdStart starts the server which serves on the following routes:

/ : Serves a HTTP home page with the server status and information about the loaded sim.
It also includes a JavaScript WebSocket client to test the server.

/ws : WebSocket endpoint for all TS2 clients and managers.
*/
func HttpdStart(addr, port string) {
	http.HandleFunc("/", serveHome)
	http.HandleFunc("/ws", serveWs)
	serverAddress := fmt.Sprintf("%s:%s", addr, port)
	log.Printf("Starting HTTP at: http://%s\n", serverAddress)
	log.Fatal(http.ListenAndServe(serverAddress, nil))
}

/*
serveHome serves the server's home page with integrated JS WebSocket client.
*/
func serveHome(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.Error(w, "Not found", 404)
		return
	}
	if r.Method != "GET" {
		http.Error(w, "Method not allowed", 405)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	data := struct {
		Title       string
		Description string
		Host        string
	}{
		sim.Options.Title,
		sim.Options.Description,
		"ws://" + r.Host + "/ws",
	}
	homeTempl.Execute(w, data)
}
