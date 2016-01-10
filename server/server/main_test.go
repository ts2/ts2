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
	"github.com/ts2/ts2/server/simulation"
	"io/ioutil"
	"net/url"
	"os"
	"testing"
)

func TestMain(m *testing.M) {
	data, _ := ioutil.ReadFile("../simulation/test_data/demo.json")
	var s simulation.Simulation
	json.Unmarshal(data, &s)
	go Run(&s, "0.0.0.0", "22222")
	os.Exit(m.Run())
}

func assertTrue(t *testing.T, expr bool, msg string) {
	if !expr {
		t.Errorf("%v: expression is false", msg)
	}
}

func assertEqual(t *testing.T, a interface{}, b interface{}, msg string) {
	if a != b {
		t.Errorf("%v: %v(%T) is not equal to %v(%T)", msg, a, a, b, b)
	}
}

func clientDial(t *testing.T) *websocket.Conn {
	u := url.URL{Scheme: "ws", Host: "127.0.0.1:22222", Path: "/ws"}
	conn, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		t.Error(err)
	}
	return conn
}

/*
login dials to the server and logs the client in
*/
func login(t *testing.T, ct ClientType, mt ManagerType, token string) (*websocket.Conn, error) {
	c := clientDial(t)
	loginRequest := RequestLogin{"Server", "login", ParamsLogin{ct, mt, token}}
	if err := c.WriteJSON(loginRequest); err != nil {
		return nil, err
	}
	var expectedResponse ResponseStatus
	c.ReadJSON(&expectedResponse)
	if expectedResponse.Data.Status == OK {
		return c, nil
	} else {
		return c, fmt.Errorf(expectedResponse.Data.Message)
	}
}
