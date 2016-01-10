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

import "encoding/json"

/*
Request is a generic request made by a websocket client.

It is used before dispatching and unmarshaling into a specific request type.
*/
type Request struct {
	Object string          `json:"object"`
	Action string          `json:"action"`
	Params json.RawMessage `json:"params"`
}

/*
ParamsLogin is the struct of the Request Params for a RequestLogin
*/
type ParamsLogin struct {
	ClientType    ClientType  `json:"type"`
	ClientSubType ManagerType `json:"subType"`
	Token         string      `json:"token"`
}

/*
RequestLogin is a request made by a websocket client to log onto the server.
*/
type RequestLogin struct {
	Object string      `json:"object"`
	Action string      `json:"action"`
	Params ParamsLogin `json:"params"`
}
