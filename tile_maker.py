import numpy as np
from stl import mesh
from PIL import Image
from PIL import ImageOps
import os
import math
import argparse


# Takes in a list of points and returns a list of triangles stitching those points together.
def stitch(p, reverse_normal=False):
    count = 0
    t = []
    for x in range(len(p) - 1):
        for y in range(len(p[0]) - 1):
            a = p[x][y]
            b = p[x + 1][y]
            c = p[x][(y + 1) % len(p[0])]
            d = p[x + 1][(y + 1) % len(p[0])]
            if reverse_normal:
                t.append([c, a, b])
                t.append([c, b, d])
            else:
                t.append([c, b, a])
                t.append([c, d, b])
            count += 1
    return t

def make_tile(front_file, back_file, x_size, y_size, thick, etch, stamp):
    # Create output directory for resultant g-code
    descriptor = os.path.basename(front_file).split(".")[0]
    folder = os.path.join('output', descriptor)
    if not os.path.isdir('output/'):
        os.mkdir('output/')
    if not os.path.isdir(folder):
        os.mkdir(folder)

    #  Open image file and convert to numpy array
    img = Image.open(front_file)
    x_res, y_res = img.size
    im = np.array(img)

    im_back = None
    if back_file != "":
        img_back = Image.open(back_file)
        img_back = img_back.resize(img.size)
        img_back = ImageOps.mirror(img_back)
        im_back = np.array(img_back)

    # Calculate the mm per step for the x and y axis
    x_step = x_size / float(x_res)
    y_step = y_size / float(y_res)

    # Data storage
    points = []
    points_inner = []
    circle = []

    # Iterate over image and calculate stl point locations
    for x in range(x_res):
        points.append([])  # The front surface
        points_inner.append([])  # The back surface

        for y in range(y_res):
            # Calculate the deflection from flat
            value = float(float(im[y, x][0]) / 255.0)
            if stamp:
                z = thick - ((value) * etch)
            else:
                z = thick - ((1.0 - value) * etch)

            # Add the etched surface point
            points[-1].append((z, x * x_step, (y_res - y) * y_step))

            # Add the un-etched surface point
            if im_back is None:
                z = 0
            else:
                value = float(float(im_back[y, x][0]) / 255.0)
                if stamp:
                    z = ((value) * etch)
                else:
                    z = ((1.0 - value) * etch)

            points_inner[-1].append((z, x * x_step, (y_res - y) * y_step))



    # Rotate etched and un-etched points 90 degrees for easy access to other edges for stitching
    points_90 = list(zip(*points[::-1]))
    points_inner_90 = list(zip(*points_inner[::-1]))

    # Stitch together faces and edges of point arrays
    triangles = stitch(points) + \
                stitch(points_inner, reverse_normal=True) + \
                stitch([points[0], points_inner[0]]) + \
                stitch([points[-1], points_inner[-1]]) + \
                stitch([points_90[0], points_inner_90[0]]) + \
                stitch([points_90[-1], points_inner_90[-1]])

    # Create the mesh by loading triangle vectors into stl object
    result = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))
    for i, t in enumerate(triangles):
        for j in range(3):
            result.vectors[i][j] = t[j]

    # Write out result
    result_file = os.path.join(folder, "%s.stl" % descriptor)
    result.save(result_file)
    return result_file


if __name__ == '__main__':
    # Get command line arguments
    parser = argparse.ArgumentParser(
        description='This application takes an depth map image, and turns it into 3d printable tile or stamp.')
    parser.add_argument('IMAGE_FILE', action="store", help='The .png or .jpg to process.')
    parser.add_argument('-b', action='store', dest='BACK', default="",
                        help='Optional texture for back of tile')
    parser.add_argument('-x', action='store', dest='X_SIZE', type=float, default=50.8,
                        help='Model X dimension in mm, default is 50.8 (2 inches)')
    parser.add_argument('-y', action='store', dest='Y_SIZE', type=float, default=50.8,
                        help='Model Y dimension in mm, default is 50.8 (2 inches)')
    parser.add_argument('-t', action='store', dest='THICK', type=float, default=3.0,
                        help='Model thickness in mm, default is 3mm')
    parser.add_argument('-e', action='store', dest='ETCH_DEEP', type=float, default=1.0,
                        help='Depth to etch surface, default is 2mm')
    parser.add_argument('--stamp', action='store_true', dest="STAMP", default=False,
                        help='Create a "negative" tile to use as a stamp')
    args = parser.parse_args()
    print make_tile(args.IMAGE_FILE, args.BACK, args.X_SIZE, args.Y_SIZE, args.THICK, args.ETCH_DEEP, args.STAMP)