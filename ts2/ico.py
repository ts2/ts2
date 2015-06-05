# -*- coding: utf-8 -*-

"""
This is a dirty hack to read icons, and avoid resource files, as we
want to share these iimages across applications, wedsite etc
"""
import os

from ts2.Qt import QtGui 


## TODO discus how to do this
ICONS_PATH = os.path.abspath( os.path.dirname( __file__ ) + "/../icons" ) 

class Ico:
    file_open = "page_go.png"
    file_save = "page_save.png"
    
    @staticmethod
    def icon(icon):
        icon_file = "%s/%s" % (ICONS_PATH, icon)
        return QtGui.QIcon( QtGui.QPixmap(icon_file) )
        
        
