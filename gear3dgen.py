'''
Gear3DGen: generate 3D OBJ files of gears according to given parameters.
Unit/dimension-agnostic.
Requires wavefront.py.
'''

import math
import wavefront

# MAIN FUNCTION
###############


def gear3dgen(innerrad,  # Inner radius (to troughs between teeth)
              outerrad,  # Outer radius (to the tips of teeth)
              teeth,  # Number of teeth
              thickness,  # In same dimension as radius
              outfile='',  # Output 3D OBJ file, auto if '', just returned content if None
              toothfunc=None,  # Function mapping teeth shape in range 0->1 to 0->1 floats
              toothpts=20,  # Number of geometry points calculated per tooth
              anglefunc=None,  # Function mapping thickness 0->1 to radian rotation
              vlayers=32,  # If anglefunc set, this determines number of vertical layers
              quiet=False,  # Enable to avoid any console output
              xyrounding=3,  # Number of decimals to round all coordinates to
              ):
    '''Main function to call: creates a gear with a specified name according to given parameters.
    If outfile=='', then the output file name will be determined automatically, but if None, no
    output file will be generated -- just its content returned by the function.

    Toothfunc expects a function (easily creatable via lambdas, e.g.), which maps each tooth's
    0->1 range to range 0->1, with 1 being the outer, and 0 the inner radius. Each tooth is
    calculated in counterclockwise direction, looking from atop.

    The gear is created laid out into X-Y dimensions, with Z as thickness.

    Anglefunc expects a function (a lambda or otherwise) which maps thickness 0->1 to angle in
    radians which rotates each layer around center vertical axis, in counterclockwise direction.
    Can be used to generate angled gears, fishbone gears, etc.
    '''

    # DATA PREPARATION

    # Filename
    if outfile == '':
        outfile = '{0}t_{1}r_{2}y.obj'.format(teeth, outerrad, thickness)

    # Tooth function - by default sinusoidal
    if toothfunc is None:
        toothfunc = g_sine

    # Tooth profile matrix (one as all teeth in profiles are identical)
    toothprofile = [toothfunc(x / toothpts) for x in range(toothpts)]
    toothprofile = [innerrad + tf * (outerrad - innerrad) for tf in toothprofile]
    gearprofile = toothprofile * teeth  # Full profile of the gear
    gearpstep = math.pi * 2 / len(gearprofile)  # Radian angle between full profile points

    # Angle function
    if not anglefunc:
        # By default, no rotation (straight spur gear), i.e. always return 0
        def anglefunc(t): return 0
        vlayers = 2  # Logical consequence: over 2 layers make no sense with spur gears
    # Layer step
    layerthickness = thickness / (vlayers - 1)  # -1 because the last layer doesn't extend

    if not quiet:
        print('Layer points:', len(gearprofile))
        print('Points among all layers:', len(gearprofile * vlayers))

    # ITERATE LAYERS, PROFILES AND POINTS

    geargeometry = []  # Collector of layers, each containing sequential (x,y,z) coordinates

    # Main iterator to add coordinates (to be stitched later)
    for layer in range(vlayers):
        layerz = layer * layerthickness  # Height at which all points will be generated
        layerprog = layer / (vlayers - 1)  # Progress of height in range 0->1
        anglebias = anglefunc(layerprog)  # Angle to add to the layer

        if not quiet:  # Report progress
            print('Calculating layer:', layer + 1, 'of', vlayers)
            print(' > Height:', layerz)
            print(' > Angle:', anglebias)

        layerpoints = []  # Local collector of (x,y,z) points per layer
        for lstep in range(len(gearprofile)):
            langle = gearpstep * lstep + anglebias  # Current point's angle
            lradius = gearprofile[lstep]  # Current radius
            # Calculate both dimensions
            lx = math.cos(langle) * lradius
            ly = math.sin(langle) * lradius
            layerpoints.append((lx, ly, layerz))

        # Add the first point to the end to stitch all in a loop
        layerpoints.append(layerpoints[0])

        # Add to master collector
        geargeometry.append(layerpoints)

    # Entire geometry (all points) calculated. Generate object
    obj3d = wavefront.wavefront(crounding=xyrounding)
    # Proceed with spur layers (sides)
    for layer in range(vlayers - 1):  # -1 because the last one does not bind further up
        if not quiet:
            print('Assembling layer', layer + 1, 'of', vlayers - 1)
        for point in range(len(gearprofile)):
            obj3d.addface(geargeometry[layer][point],
                          geargeometry[layer][point + 1],
                          geargeometry[layer + 1][point + 1])
            obj3d.addface(geargeometry[layer][point],
                          geargeometry[layer + 1][point + 1],
                          geargeometry[layer + 1][point])

    # Close floor and ceiling
    for point in range(len(gearprofile)):
        # Floor
        obj3d.addface(geargeometry[0][point + 1],
                      geargeometry[0][point],
                      (0, 0, 0))
        # Ceiling
        obj3d.addface(geargeometry[-1][point],
                      geargeometry[-1][point + 1],
                      (0, 0, thickness))

    # Write to file (unless specifically rejected)
    return obj3d.save(outfile, returnonly=(outfile is None))

# GEAR TOOTH & ANGLE DEFINITION HELPERS IN RANGE 0->1
#####################################################


def g_vshape(x):  # V-shaped
    return abs(0.5 - x) * 2


def g_ashape(x):  # A (or capital lambda) shaped
    return 1 - g_vshape(x)


def g_sine(x):  # Sinusoidal (default tooth)
    return math.cos(x * math.pi * 2) / 2 + 0.5


def g_halfsine(x):  # Undercut half-sinusoidal
    return max([math.cos(x * math.pi * 2), 0])

### SELF-TEST EXAMPLES
######################


if __name__ == '__main__':
    ...
    gear3dgen(2,18,10,32,toothpts=20,anglefunc=lambda x:1/(x*4+0.3)**2,vlayers=40)
    # gear3dgen(2,18,10,32,toothpts=20,anglefunc=lambda x:math.sin(2*x*6.28)/4,vlayers=40)
    # gear3dgen(16, 20, 32, 5, toothfunc=g_halfsine, anglefunc=lambda x: x / 12)
    # gear3dgen(20, 24, 12, 4, anglefunc=lambda x: x / 8, vlayers=8)
    # gear3dgen(14, 16, 16, 4, anglefunc=g_vshape, vlayers=7)
