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

type StatusCode string

const (
	OK StatusCode = "OK"
	KO StatusCode = "KO"
)

type MessageType string

const (
	RESPONSE MessageType = "response"
	EVENT    MessageType = "event"
	REQUEST  MessageType = "request"
)

type StatusData struct {
	Status  StatusCode `json:"status"`
	Message string     `json:"message"`
}

/*
StatusResponse is a status message sent to a websocket client
*/
type StatusResponse struct {
	MsgType MessageType `json:"msgType"`
	Data    StatusData  `json:"data"`
}
