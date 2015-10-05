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

import sys
import optparse

if __name__ == '__main__':

    if not sys.version_info >= (3, 0, 0):
        sys.exit("ERROR: TS2 requires python3")

    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug", dest="debug", help="Start in debug mode", action="store_true", default=False)
    (options, args) = parser.parse_args()

    file = None
    if len(args) > 0:
        file = args[0]

    import ts2.application
    ts2.application.Main(debug=options.debug, file=file)
