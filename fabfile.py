# -*- coding: utf-8 -*-

import os

from fabric.api import env, local, run, cd, lcd, sudo, warn_only, prompt

import ts2

HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))

TEMP_LOCAL = HERE_PATH + "/temp"

DOCS_WWW_GIT = "ssh://5570e9ce5973ca4a1a000006@docs-ts2.rhcloud.com/~/git/docs.git/" 
DOCS_WWW_DIR =  "docs-ts2.rhcloud.comz"
DOCS_TEMP_DIR = TEMP_LOCAL + "/" + DOCS_WWW_DIR

def clean():
	local("rm ./docs/_static/favicon.*")
	local("rm -f -r temp/*")

def build_docs():
	"""Builds the documentation"""
	
	# copy some stuff
	local("cp ./images/favicon.* ./docs/_static/")
	local("cp ./images/banner.jpeg ./docs/_static/")
	
	## run build
	local("/usr/bin/python3 /usr/local/bin/sphinx-build -b html ./docs/ ./temp/docs_build")
	
	
def init():
	"""Initialize the local env"""
	local("mkdir -p %s" % TEMP_LOCAL)
	
	if os.path.exists(DOCS_TEMP_DIR):
		print DOCS_TEMP_DIR , "exists"
	else:
		with lcd(TEMP_LOCAL):
			local( "git clone %s %s" % (DOCS_WWW_GIT, DOCS_WWW_DIR) )
		