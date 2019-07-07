#!/usr/bin/python3
#
#   Copyright (C) 2008-2015 by Nicolas Piganeau
#   npi@m4x.org
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import argparse
import sys
import os

import websocket

if __name__ == '__main__':

    if not sys.version_info >= (3, 0, 0):
        sys.exit("ERROR: TS2 requires Python3")

    parser = argparse.ArgumentParser("ts2")
    parser.add_argument("-s", "--server", dest="server",
                        help="Path to ts2-sim-server", action="store", default=None)
    parser.add_argument("-d", "--debug", dest="debug",
                        help="Start with debug mode", action="store_true",
                        default=False)
    parser.add_argument("-e", "--edit", dest="edit", help="Open sim in editor",
                        action="store_true", default=False)
    parser.add_argument("file", help=".ts2 file to open/edit", type=str,
                        nargs='?')
    args = parser.parse_args()

    if args.edit and args.file is None:
        sys.exit("ERROR: Need a file with -e option")

    if args.server and not os.path.exists(args.server):
        sys.exit("ERROR: Path to ts-sim-server not at `%s`" % args.server)

    import ts2.application
    ts2.application.Main(args=args)
