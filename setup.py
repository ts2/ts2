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

from setuptools import setup, find_packages
from ts2 import __APP_SHORT__, __APP_LONG__, __VERSION__, __PROJECT_WWW__, \
    __ORG_NAME__, __ORG_CONTACT__, __APP_DESCRIPTION__

setup(
    name=__APP_SHORT__,
    url=__PROJECT_WWW__,
    author=__ORG_NAME__,
    author_email=__ORG_CONTACT__,
    maintainer=__ORG_NAME__,
    maintainer_email=__ORG_CONTACT__,
    description=__APP_DESCRIPTION__,
    long_description=__APP_DESCRIPTION__,
    license="GPL License",
    version=__VERSION__,
    packages=find_packages(),
    install_requires=[
        "simplejson >= 3.2", 'websocket'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment :: Simulation",
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: Polish",
    ],
)
