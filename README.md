# SVG2SHP Light
SVG2SHP Light is a simple and light SVG to SHP (ESRI) converter.
Please note:

    1. It converting only polygons and polylines. Circles, rectangles and etc svg-objects are not supported and ignored.
    2. Closed svg-objects with not null fill converting to polygons.
    3. All other objects converting to lines.
    4. CSS Styles are not supported and ignored.
    5. All polygons in shapefile have fill attribute in dbf table.
    6. Lines have stroke attribute if dbf table if it available in svg-file. 
    7. Coordinate systems are not supported (for now). Use vector transformations in your GIS.
    8. All commits are welcome.