# -*- coding: utf-8 -*-

import os

from fabric.api import env, local, run, cd, lcd, sudo, warn_only, prompt

os.environ["__GEN_DOCS__"] = "1"

import ts2

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))

TEMP_LOCAL = HERE_PATH + "/temp"

DOCS_WWW_GIT = "ssh://5570e9ce5973ca4a1a000006@docs-ts2.rhcloud.com/~/git/docs.git/" 
DOCS_WWW_DIR =  "docs-ts2.rhcloud.comz"
DOCS_TEMP_DIR = TEMP_LOCAL + "/" + DOCS_WWW_DIR

def docs_server(port=8080):
    """Run local HTTP server with docs"""
    with lcd(TEMP_LOCAL + "/docs_build"):
        local("python -m SimpleHTTPServer %s" % port)

def docs_clean():
    """Clean current docs-build """
    local("rm ./docs/_static/favicon.*")
    local("rm -f -r temp/*")

def docs_build():
    """Build the documentation to temp/docs_build"""

    # copy some stuff
    local("cp ./images/favicon.* ./docs/_static/")
    local("cp ./images/favicon-ani.* ./docs/_static/")
    local("cp ./images/banner.jpeg ./docs/_static/")
    local("cp ./images/screenshot.jpeg ./docs/_static/")

    ## run build
    local("/usr/bin/python3 /usr/local/bin/sphinx-build -a  -b html ./docs/ ./temp/docs_build")

def docs_update_www():
    """Copies build over to http://docs-ts2.rhcloud.com/.git and push online"""

    # nuke all stuff in openshift dir as its olde eg dead files et all
    with lcd(DOCS_TEMP_DIR):
        ## nuke dirs
        for d in ["_static", "_sources", "_modules", "api"]:
            local("rm -f -r %s" % d)
        local("rm -f -r *.html")
        local("rm -f -r *.js")

    ## copy the compiled docs across
    with lcd(TEMP_LOCAL):
        local("cp -r docs_build/* %s" % (DOCS_WWW_DIR) )

    ## push to openshift
    with lcd(DOCS_TEMP_DIR):
        local( "git add ." )
        local( 'git commit -a -m "Update" ' )
        local( "git push origin master" )


def init():
    """Initialize the local env"""
    local("mkdir -p %s" % TEMP_LOCAL)

    if os.path.exists(DOCS_TEMP_DIR):
        print DOCS_TEMP_DIR , "exists"
    else:
        with lcd(TEMP_LOCAL):
            local( "git clone %s %s" % (DOCS_WWW_GIT, DOCS_WWW_DIR) )

