

from ts2.Qt import QtCore, Qt

import ts2.utils

class XSettings(QtCore.QSettings):
    
    def __init__(self):
        super().__init__()
        
        
    #def recent_files(self):
        
    
    def get_recent(self):
        """List of recent files
        
        :rtype: lst of str's
        """
        s = self.value("recent")
        if s == None or s == "":
            return []
        print (s)
        return ts2.utils.from_json(s)
        
            
    def add_recent(self, file_path):
        """Add a recent file"""
        lst = self.get_recent()
        if file_path in lst:
            # already in so move to front
            lst.remove(file_path)
        # insert at front
        lst.insert(0, file_path)
        self.setValue("recent", ts2.utils.to_json(lst))
        return lst
    
    
    def save_window( self, window ):
        #   settings.setValue("geometry", saveGeometry());
        #   settings.setValue("windowState", saveState());
     
        self.setValue( "window/%s/geometry" % window.W_NAME, window.saveGeometry()  )
        self.setValue( "window/%s/state" % window.W_NAME, window.saveState()  )
        
    def restore_window( self, window ):
        v = self.value( "window/%s/geometry" % window.W_NAME )
        if v == None:
            return
        window.restoreGeometry(  v )
        
        v = self.value( "window/%s/state" % window.W_NAME )
        if v == None:
            return
        window.restoreState(  v )

    def save_splitter( self, window, splitter ):
        self.settings.setValue( "window/%s/splitter" % window.W_NAME,  splitter.saveState()  )
        
    def restore_splitter( self, window, splitter ):
        splitter.restoreState( self.settings.value( "window/%s/splitter" % window.W_NAME ).toByteArray() )

    def save_tree( self, tree ):
        self.settings.setValue( "tree/%s" % tree._settings_ki,  tree.header().saveState()  )
        
    def restore_tree( self, tree ):
        tree.header().restoreState( self.settings.value("tree/%s" % tree._settings_ki ).toByteArray() )
        