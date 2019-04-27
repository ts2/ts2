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

from Qt import QtCore, QtWidgets, Qt


class EditorSceneBackground(QtWidgets.QGraphicsRectItem):
    """The EditorSceneBackground is a graphics item set at the background of
    the editor scene to handle drag and drop events."""

    def __init__(self, editor, x, y, width, height):
        """Constructor for the EditorSceneBackground class"""
        super().__init__(x, y, width, height)
        self.setZValue(-100)
        self.setAcceptDrops(True)
        self.editor = editor
        # pen = QtGui.QPen(Qt.cyan)
        # self.setPen(pen)

    def dragEnterEvent(self, event):
        """dragEnterEvent handler for the EditorSceneBackground."""
        if event.mimeData().hasText():
            event.accept()
            self.update()

    def dragMoveEvent(self, event):
        """dragMoveEvent handler for the EditorSceneBackground."""
        if event.mimeData().hasText():
            tiType, tiId, ox, oy, point = event.mimeData().text().split("#")
            if not tiId.startswith("__EDITOR__"):
                clickPos = QtCore.QPointF(float(ox), float(oy))
                self.editor.moveTrackItem(tiId, event.scenePos(),
                                          clickPos, point)

    def dropEvent(self, event):
        """dropEvent handler for the EditorSceneBackground.
        If the dragged item is already on this scene, it moves the item.
        If the dragged item is dragged from the library scene, a new item is
        created."""
        if event.mimeData().hasText():
            tiType, tiId, ox, oy, point = event.mimeData().text().split("#")
            if tiId.startswith("__EDITOR__"):
                event.setDropAction(Qt.CopyAction)
                event.accept()
                self.editor.createTrackItem(tiType, event.scenePos())
            else:
                event.setDropAction(Qt.MoveAction)
                event.accept()
                clickPos = QtCore.QPointF(float(ox), float(oy))
                self.editor.moveTrackItem(tiId, event.scenePos(),
                                          clickPos, point)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        """Event handler for the mousePressEvent. Empties the current item
        selection if right button clicked."""
        if event.buttons() == Qt.RightButton:
            self.editor.clearSelection()
        super().mousePressEvent(event)
