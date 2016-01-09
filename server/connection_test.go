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
	"encoding/json"
	"github.com/gorilla/websocket"
	"testing"
	"time"
)

func TestLogin(t *testing.T) {
	runServer(t)
	// Wait for server to come up
	time.Sleep(100 * time.Millisecond)
	c := clientDial(t)
	defer func() {
		c.Close()
	}()

	// Try to send something that is not a login request
	badRequest := Request{"Dummy", "dummy", json.RawMessage{}}
	if err := c.WriteJSON(badRequest); err != nil {
		t.Error(err)
	}
	var expectedResponse ResponseStatus
	c.ReadJSON(&expectedResponse)
	assertEqual(t, expectedResponse, ResponseStatus{RESPONSE, DataStatus{KO, "Error: Client should call Server/login before all other requests"}}, "Login/Incorrect")
	_, _, err := c.ReadMessage()
	if _, ok := err.(*websocket.CloseError); err == nil || !ok {
		t.Errorf("Login/Incorrect/Connection should be closed")
	}
	c.Close()

	// Correct login
	c = clientDial(t)
	loginRequest := RequestLogin{"Server", "login", ParamsLogin{CLIENT, "", "client-secret"}}
	if err := c.WriteJSON(loginRequest); err != nil {
		t.Error(err)
	}
	c.ReadJSON(&expectedResponse)
	assertEqual(t, expectedResponse, ResponseStatus{RESPONSE, DataStatus{OK, ""}}, "Login/Correct")
}
