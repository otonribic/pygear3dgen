# pygear3dgen
A pure Python library that generates various types of gears according to parameters in a function, and exports it to ubiquitous Wavefront (.OBJ) file that can be used elsewhere.
Specify inner and outer radii, thickness, tooth shape function, rotation (shape), etc. and have a gear 3D file generated - as simple as that.

E.g. gear3dgen(20, 24, 12, 4, anglefunc=lambda x: x / 8, vlayers=8)
...creates a gear with inner radius of 20, outer of 24, with 12 teeth, thick 4, angled, with vertical resolution of 8 layers.

When dealing with angled (or fishbone-style) gears, the gear generation can be a bit slow, as the involved geometry has to deal with some complex surfaces.
