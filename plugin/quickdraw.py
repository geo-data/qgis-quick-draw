# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickDraw
                                 A QGIS plugin
 Draw a bounding box on the canvas
                              -------------------
        begin                : 2014-05-16
        copyright            : (C) 2014 by Homme Zwaagstra
        email                : hrz@geodata.soton.ac.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from quickdrawdialog import QuickDrawDialog
import os.path

from random import uniform
from itertools import izip

class QuickDrawError(Exception):
    def __init__(self, message, title):
        super(QuickDrawError, self).__init__(message)
        self.title = title

class InvalidGeometry(QuickDrawError):
    def __init__(self, geom):
        if len(geom) > 50:
            msg = geom[:24].rstrip() + ' ... ' + geom[-24:].lstrip()
        else:
            msg = geom
        super(InvalidGeometry, self).__init__("The geometry formatting is wrong: %s" % msg, 'Invalid Geometry')
        self.geom = geom

class QuickDraw:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'quickdraw_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = QuickDrawDialog()

        # the draw stack contains references to all items drawn by the plugin
        self.drawStack = []

        # has the applied button been clicked?
        self.applied = False

        # should the geometry input text be cached
        self._cache_text = True

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/quickdraw/icon.png"),
            u"Quick Draw", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Quick Draw", self.action)

        QObject.connect(self.dlg.clearButton, SIGNAL("clicked()"), self.clearButtonClicked)
        self.dlg.buttonBox.clicked.connect(self.buttonBoxClicked)
        self.dlg.exampleComboBox.activated.connect(self.exampleSelected)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Quick Draw", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.removeItems()

    def buttonBoxClicked(self, button):
        button_text = str(button.text())
        if button_text == 'Apply':
            self.draw()
            self.applied = True
        elif button_text == 'Reset':
            self.resetText()

    def clearButtonClicked(self):
        self.dlg.geometryTextEdit.setPlainText('')

    def exampleSelected(self, index):
        """
        Create geometry examples based on the current extent
        """
        canvas = self.iface.mapCanvas()
        extent = canvas.extent()
        minx = extent.xMinimum()
        miny = extent.yMinimum()
        maxx = extent.xMaximum()
        maxy = extent.yMaximum()

        if index == 0:          # bounding box
            text = "%s,%s : %s,%s" % (minx, miny, maxx, maxy)
        elif index == 1:        # point
            x = uniform(minx, maxx)
            y = uniform(miny, maxy)
            text = '%s,%s' % (x, y)
        elif index == 2:        # line
            x, y = [], []
            for i in range(3):
                x.append(uniform(minx, maxx))
                y.append(uniform(miny, maxy))
            text = ','.join(('%s,%s' % t for t in izip(sorted(x), y)))
        else:                   # polygon
            x, y = [], []
            for i in range(4):
                x.append(uniform(minx, maxx))
                y.append(uniform(miny, maxy))
            x.sort()
            x.append(x[0])
            y.append(y[0])
            text = ','.join(('%s,%s' % t for t in izip(x, y)))

        self.dlg.geometryTextEdit.appendPlainText(text)

    def draw(self, checkZoom = True):
        text = str(self.dlg.geometryTextEdit.toPlainText())

        drawStack = []
        for line in [l.strip() for l in text.splitlines()]:
            if not line: continue

            try:
                geom = self.textToGeometry(line)
                r = self.geometryToCanvas(geom)
                r.show()
                drawStack.append(r)
            except QuickDrawError, e:
                message = e.message + "\n\nUse the QGIS \"What's This?\" help tool to click on the text input box for information on how to correctly format geometries."
                QMessageBox.warning(self.dlg, e.title, message)
                self.removeItems(drawStack) # remove added items
                return False

        self.removeItems()  # remove previous items
        self.drawStack = drawStack

        # zoom to the geometries
        if checkZoom and self.dlg.zoomCheckBox.isChecked():
            self.zoomToItems()

        return True

    def resetText(self):
        self.dlg.geometryTextEdit.setPlainText(self.text)

    # run method that performs all the real work
    def run(self):
        # save the text so that it can be reverted in case of cancel
        if self._cache_text:
            self.text = self.dlg.geometryTextEdit.toPlainText()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            if not self.draw():
                # try again (without caching the bad text)
                self._cache_text = False
                self.run()
                self._cache_text = True
                return
        else:
            # cancel was pressed: ensure the text doesn't change...
            self.resetText()

            #...and ensure any apply operations are reverted
            if self.applied:
                self.draw(False)
                self.applied = False

    def zoomToItems(self):
        def getBBOX(item):
            if isinstance(item, QgsVertexMarker):
                return QgsRectangle(item.point, item.point)
            return item.asGeometry().boundingBox()
        
        if not self.drawStack:
            return

        canvas = self.iface.mapCanvas()
        extent = getBBOX(self.drawStack[0])
        for item in self.drawStack[1:]:
            bbox = getBBOX(item)
            extent.combineExtentWith(bbox)

        if extent:
            canvas.setExtent(extent)
            canvas.updateFullExtent()

    def removeItems(self, drawStack = None):
        if drawStack is None:
            drawStack = self.drawStack

        # Remove all items from the canvas
        scene = self.iface.mapCanvas().scene()
        while drawStack:
            scene.removeItem(drawStack.pop())

    def textToCoords(self, text):
        def toCoords(text):
            try:
                coords = [float(t.strip()) for t in text.split(',')]
            except ValueError:
                raise InvalidGeometry(text)

            if not len(coords) % 2: # we have an even number of coordinates
                x = None
                points = []
                for i, coord in enumerate(coords):
                    if i % 2:
                        points.append((x, coord))
                    else:
                        x = coord
                return points

            raise QuickDrawError('An even number of coordinates is expected but %d were input.' % len(coords), 'Invalid Coordinate Count')

        if ':' in text:
            # it's a bbox
            try:
                minc, maxc = text.split(':')
                minx, miny = toCoords(minc)[0]
                maxx, maxy = toCoords(maxc)[0]
            except ValueError:
                raise InvalidGeometry(text)
                
            return [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]
        
        # it's a normal coordinate string
        return toCoords(text)

    def coordsToPoints(self, coords):
        return [QgsPoint(*coord) for coord in coords]

    def textToGeometry(self, text):
        coords = self.textToCoords(text)
        coord_count = len(coords)
        points = self.coordsToPoints(coords)

        if coord_count == 1:
            return points[0]
        elif coord_count > 2 and coords[0] == coords[-1]:
            # it's a polygon
            return QgsGeometry.fromPolygon([points])
        
        return QgsGeometry.fromPolyline(points)

    def geometryToCanvas(self, geom):
        if isinstance(geom, QgsPoint):
            r = self.pointToVertexMarker(geom)
        else:
            r = self.geometryToRubberBand(geom)
        
        r.setColor(QColor(255,0,0))
        r.setOpacity(0.5)
        return r

    def pointToVertexMarker(self, point):
        canvas = self.iface.mapCanvas()
        m = QgsVertexMarker(canvas)
        m.setCenter(point)
        m.setPenWidth(2.5)
        m.point = point         # save the original point for use in zooming
        return m
        
    def geometryToRubberBand(self, geom):
        canvas = self.iface.mapCanvas()
        r = QgsRubberBand(canvas, False)
        r.setToGeometry(geom, None)
        r.setWidth(2.5)
        return r
