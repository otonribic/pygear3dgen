'''
Module to create Wavefront3D object files simply.
Just adding faces with 3 sets of X-Y-Z vertices. Chosen whether 1- or 2-sided.
'''


class wavefront:  # Master class

    def __init__(self,
                 doubleface=False,  # Whether to have all faces 2-sided by default
                 crounding=3,  # How many decimals to round the vertices to
                 ):
        self.vertices = []  # Collector of X-Y-Z's
        self.verticeset = set()  # X-Y-Z vertex set
        self.faces = []  # Collector of 3-grams
        self.doubleface = doubleface  # Always generate double faces by default?
        self.crounding = crounding  # Rounded to the number of decimals

    def addvertex(self, x, y, z):  # Add vertex if not already there (for any reason)
        x, y, z = (round(float(x), self.crounding),
                   round(float(y), self.crounding),
                   round(float(z), self.crounding))
        if (x, y, z) not in self.verticeset:
            self.vertices.append((x, y, z))
            self.verticeset.add((x, y, z))
        return self.vertices.index((x, y, z))

    def addface(self, *args):  # Either three X-Y-Z lists or everything unpacked (triangle)
        args = list(args)
        if len(args) == 9:
            # Condense into three tuples
            args = [(args[0], args[1], args[2]),
                    (args[3], args[4], args[5]),
                    (args[6], args[7], args[8])]

        # No coordinates?
        if len(args) != 3:
            raise ReferenceError

        # Normalize
        for d in [0, 1, 2]: args[d] = tuple(args[d])

        # Add necessary vertices
        triangle = [0, 0, 0]  # Placeholder of triangle
        for d in [0, 1, 2]:
            triangle[d] = self.addvertex(*args[d])

        # Add a face
        self.faces.append(tuple(triangle))
        if self.doubleface:
            triangle.reverse()
            self.faces.append(tuple(triangle))

    def addquad(self, *args):  # Either four X-Y-Z lists or everything unpacked (quadrangle)
        if len(args) == 12:
            # Condense
            args = [(args[0], args[1], args[2]),
                    (args[3], args[4], args[5]),
                    (args[6], args[7], args[8]),
                    (args[9], args[10], args[11])]

        # No coordinates?
        if len(args) != 4:
            raise ReferenceError

        # Add two triangles
        self.addface(args[0], args[1], args[2])
        self.addface(args[0], args[2], args[3])

    # Export to file

    def save(self,
             filename='wavefront.obj',  # Output file
             zoom=(1, 1, 1),  # Multipliers of output
             offset=(0, 0, 0),  # Offset the model
             returnonly=False, # If enabled, only return file content, no file writing
             ):
        # Assemble the file content
        lines = ['o mainobject\n']
        for vt in self.vertices:
            lines.append(f'v {vt[0]*zoom[0]+offset[0]} {vt[1]*zoom[1]+offset[1]} {vt[2]*zoom[2]+offset[2]}\n')
        lines.append('s off\n')
        for tr in self.faces:
            lines.append(f'f {tr[0]+1} {tr[1]+1} {tr[2]+1}\n')
        lines = ''.join(lines)

        if not returnonly:
            outf = open(filename, 'w', encoding='utf8')
            outf.write(lines)
            outf.close()

        return lines


# Self-test
# ---------
if __name__ == '__main__':
    wf = wavefront()
    print(wf)
    wf.addvertex(1, 2, 3)
    wf.addface(1, 2, 3, 4, 5, 6, 7, 8, 9)
    wf.addface(1, 2, 3, 4, 5, 6, 10, 11, 12)
    wf.save()
