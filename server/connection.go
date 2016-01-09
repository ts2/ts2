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
	"fmt"
	"github.com/gorilla/websocket"
	"log"
)

type ClientType string

const (
	CLIENT  ClientType = "client"
	MANAGER ClientType = "manager"
)

type ManagerType string

const (
	TRAIN_MANAGER     ManagerType = "train"
	ROUTE_MANAGER     ManagerType = "route"
	TRACKITEM_MANAGER ManagerType = "trackItem"
	ARS_MANAGER       ManagerType = "ars"
)

func (mt ManagerType) isManagerType() bool {
	if mt == TRAIN_MANAGER ||
		mt == ROUTE_MANAGER ||
		mt == TRACKITEM_MANAGER ||
		mt == ARS_MANAGER {
		return true
	}
	return false
}

/*
connection is a wrapper around the websocket.Conn
*/
type connection struct {
	websocket.Conn
	// pushChan is the channel on which pushed messaged are sent
	pushChan    chan []byte
	clientType  ClientType
	ManagerType ManagerType
}

/*
loginClient waits for a login request from the client, checks it and registers the connection
on the hub if it is valid. Otherwise it returns an error.
*/
func (conn *connection) loginClient() error {
	req := new(Request)
	if err := conn.ReadJSON(req); err != nil {
		return err
	}
	if req.Object != "Server" || req.Action != "login" {
		return fmt.Errorf("Client should call Server/login before all other requests")
	}

	loginParams := ParamsLogin{}
	if err := json.Unmarshal(req.Params, &loginParams); err != nil {
		return fmt.Errorf("Unable to parse login params: %s", err)
	}

	if loginParams.ClientType == CLIENT &&
		loginParams.Token == sim.Options.ClientToken {
		conn.clientType = CLIENT
	} else if loginParams.ClientType == MANAGER &&
		loginParams.Token == sim.Options.ManagerToken &&
		loginParams.ClientSubType.isManagerType() {
		conn.clientType = MANAGER
		conn.ManagerType = loginParams.ClientSubType
	} else {
		return fmt.Errorf("Invalid login parameters")
	}
	conn.writeOk()
	ts2Hub.registerChan <- conn
	log.Printf("%s: logged in as %s %s", conn.RemoteAddr(), conn.clientType, conn.ManagerType)
	return nil
}

/*
writeError sends an error message to the client as a response to its request.
*/
func (conn *connection) writeError(e error) error {
	sr := ResponseStatus{
		MsgType: RESPONSE,
		Data: DataStatus{
			KO,
			fmt.Sprintf("Error: %s", e),
		},
	}
	return conn.WriteJSON(&sr)
}

/*
writeOk sends a OK status message to the client as a response to its request
*/
func (conn *connection) writeOk() error {
	sr := ResponseStatus{
		MsgType: RESPONSE,
		Data: DataStatus{
			OK,
			"",
		},
	}
	return conn.WriteJSON(&sr)
}
