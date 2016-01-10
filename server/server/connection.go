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
	pushChan    chan interface{}
	clientType  ClientType
	ManagerType ManagerType
	LastRequest Request
}

/*
loop starts the reading and writing loops of the connection.
*/
func (conn *connection) loop() {
	if err := conn.loginClient(); err != nil {
		// Try to notify client
		conn.WriteJSON(NewErrorResponse(err))
		log.Println(err)
		return
	}
	go conn.processWrite()
	conn.processRead()
}

/*
processRead performs all read operations from the connection and forwards to the hub
*/
func (conn *connection) processRead() {
	for {
		err := conn.ReadJSON(&conn.LastRequest)
		if err != nil {
			if _, ok := err.(*websocket.CloseError); ok {
				log.Printf("%s: Connection closed by peer", conn.RemoteAddr())
				conn.Close()
			} else {
				log.Printf("%s: Error while reading: %s", conn.RemoteAddr(), err)
				conn.pushChan <- NewErrorResponse(err)
			}
		} else {
			hub.readChan <- conn
		}
	}
}

/*
processWrite performs all the write operations to the connection sent by the hub
*/
func (conn *connection) processWrite() {
	for {
		req := <-conn.pushChan
		if err := conn.WriteJSON(req); err != nil {
			log.Printf("%s: Error while writing %+v: %s", conn.RemoteAddr(), req, err)
		}
	}
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
		return fmt.Errorf("%s: Client should call Server/login before all other requests", conn.RemoteAddr())
	}

	loginParams := ParamsLogin{}
	if err := json.Unmarshal(req.Params, &loginParams); err != nil {
		return fmt.Errorf("%s: Unable to parse login params: %s", conn.RemoteAddr(), err)
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
		return fmt.Errorf("%s: Invalid login parameters", conn.RemoteAddr())
	}
	if err := conn.WriteJSON(NewOkResponse()); err != nil {
		log.Printf("%s: Error while writing: %s", conn.RemoteAddr(), req, err)
	}
	hub.registerChan <- conn
	log.Printf("%s: logged in as %s %s", conn.RemoteAddr(), conn.clientType, conn.ManagerType)
	return nil
}

/*
Close ends the connection and closes associated resources
*/
func (conn *connection) Close() error {
	hub.unregisterChan <- conn
	conn.Conn.Close()
	close(conn.pushChan)
	return nil
}
