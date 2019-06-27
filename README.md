# Tile Maker
Turns a .jpg or .png depth map into a 3d printable tile with that depth map etched into the surface.

**Usage:**

tile_maker.py [-x X_SIZE] [-y Y_SIZE] [-t THICK] [-e ETCH_DEEP]
                     [--stamp]
                     IMAGE_FILE

IMAGE_FILE    The .png or .jpg to process.

-h, --help    show this help message and exit

-x X_SIZE     Model X dimension in mm, default is 50.8 (2 inches)

-y Y_SIZE     Model Y dimension in mm, default is 50.8 (2 inches)

-t THICK      Model thickness in mm, default is 3mm

-e ETCH_DEEP  Depth to etch surface, default is 2mm

--stamp       Create a "negative" tile to use as a stamp


