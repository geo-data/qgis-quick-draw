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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load QuickDraw class from file QuickDraw
    from quickdraw import QuickDraw
    return QuickDraw(iface)
