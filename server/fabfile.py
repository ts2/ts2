# -*- coding: utf-8 -*-

import os

from fabric.api import env, local, run, cd, lcd, sudo, warn_only, prompt

os.environ["__GEN_DOCS__"] = "1"


HERE_PATH =  os.path.abspath( os.path.dirname( __file__ ))

def c_tpl():
    """Compile templates"""
    local("go-bindata -debug -pkg server -o server/bindata_templates.go templates/")
    
    
def run_dev():
    """Launch and compile local development golang server"""
    local("go run main.go ./simulation/test_data.json")
    