# Quick Draw

A [QGIS](http://www.qgis.org) plugin that allows users to input and display
simple geometries on the map canvas.

Geometries are entered as coordinate strings and are rendered directly to the
map canvas.  This makes the plugin suitable for quickly viewing bounding boxes,
points and lightweight lines and polygons.

It is important to note that because the geometries are rendered directly to
the map canvas they are *not* saved as layers or any other persistent format.
Therefore when QGIS is closed or the plugin is de-activated the geometries
disappear.  This means Quick Draw is suitable as a basic scratch editor and
visualiser for geometries.

## Usage

The plugin requires QGIS v2.0 or greater.

1. Use the plugin manager to find and install the Quick Draw plugin from the
   QGIS plugins repository.

2. Click on the Quick Draw toolbar icon to bring up the Quick Draw dialog.

3. Enter and edit your geometries in the text area.

4. Optionally uncheck the `Zoom to geometries` checkbox if you do not want the
   map to zoom in to the combined extent of the geometries you have just
   entered.

5. Click `OK`.

6. Optionally activate the tool again to edit, remove and add to your Quick
   Draw geometries.

### Editing Geometries

Geometries can be input as **points**, **polylines**, **polygons** and
**bounding boxes** in the following formats:

**Points**: *x,y*

**Polylines** and **polygons**: *x1,y1,x2,y2,x3,y3 etc.*

**Bounding box**: *xmin,ymin : xmax,ymax*

Coordinates are comma separated (whitespace is ignored). It is assumed that
coordinates are entered in the same **projection** as the map.

The difference between a polyline and a polygon is that in a polygon the final
coordinate pair must match the initial coordinate pair, thus closing the
line. Complex polygons with holes are not supported. The bounding box format is
shorthand for creating a rectangular polygon, and is the same format as that
used for the QGIS extents shown in the status bar.

**Multiple geometries** are supported: there is one geometry per line.

**Deleting** or **editing** geometries and pressing `OK` will update the
  canvas.

### Help

When using the plugin, clicking on the geometry text input box with the QGIS
**What's this?** help tool will display the geometry editing information from
the previous section.

## Installation from Source

The recommended way to install the plugin is to the plugin manager as described
above.  However, the plugin can be installed from source, which is useful if
you want the very latest changes.  This method requires that you have GNU
`make`, `pyrcc4` and `pyuic4` installed.

1. Download or checkout the source code from Github.

2. Change to the `plugin` directory in the downloaded source package and type
   `make deploy`.

3. Start QGIS.  You should find the Quick Draw plugin listed in the plugin
   manager.

