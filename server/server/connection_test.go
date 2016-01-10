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
	"encoding/json"
	"fmt"
	"github.com/gorilla/websocket"
	"testing"
	"time"
)

func TestLogin(t *testing.T) {
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
	expectedErrorMsg := fmt.Sprintf("Error: %s: Client should call Server/login before all other requests", c.LocalAddr())
	assertEqual(t, expectedResponse, ResponseStatus{RESPONSE, DataStatus{KO, expectedErrorMsg}}, "Login/Wrong request")
	_, _, err := c.ReadMessage()
	if _, ok := err.(*websocket.CloseError); err == nil || !ok {
		t.Errorf("Login/Wrong request/Connection should be closed")
	}
	c.Close()

	// Incorrect login
	c, err = login(t, CLIENT, "", "wrong-token")
	expectedErrorMsg = fmt.Sprintf("Error: %s: Invalid login parameters", c.LocalAddr())
	if err == nil || err.Error() != expectedErrorMsg {
		t.Errorf("Login/Incorrect: Unexpected behaviour")
	}
	_, _, err = c.ReadMessage()
	if _, ok := err.(*websocket.CloseError); err == nil || !ok {
		t.Errorf("Login/Wrong request/Connection should be closed")
	}
	c.Close()

	// Correct login
	if _, err = login(t, CLIENT, "", "client-secret"); err != nil {
		t.Errorf(err.Error())
	}
}

func TestDoubleLogin(t *testing.T) {
	// Wait for server to come up
	time.Sleep(100 * time.Millisecond)
	c, err := login(t, CLIENT, "", "client-secret")
	defer func() {
		c.Close()
	}()

	if err != nil {
		t.Errorf(err.Error())
	} else {
		c.WriteJSON(RequestLogin{"Server", "login", ParamsLogin{CLIENT, "", "client-secret"}})
		var expectedResponse ResponseStatus
		c.ReadJSON(&expectedResponse)
		if expectedResponse.Data.Status != KO {
			fmt.Errorf("Double login: should have failed")
		} else if expectedResponse.Data.Message != "Error: Can't call login when already logged in" {
			fmt.Errorf("Double login: Wrong error message")
		}
	}
}
