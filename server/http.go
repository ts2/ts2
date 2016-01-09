
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
It also includes a JavaScript WebSocket client to communicate and manage the server.

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
serveHome() serves the html home.html page with integrated JS WebSocket client.
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
