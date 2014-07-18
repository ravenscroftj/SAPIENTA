"""
Test to see if foo_split.xml is the same as foo_annotated.xml when you 
remove the <text> tags and the <CoreSc1> tags. That is, check that the 
annotation process has not removed any sentences or mangled the doc.

Will output any lines that are different.
"""


import sys

def readfiles(basename):
    f1 = open(basename+"_split.xml")
    f2 = open(basename+"_annotated.xml")

    c1 = f1.readline()
    c2 = f2.readline()
    while c1:
        c2 = c2.replace("<text>","")
        c2 = c2.replace("</text>","")
        dirty = True
        while dirty:
            loc = c2.find("<CoreSc1")
            if loc == -1:
                if c1 != c2:
                    print c1
                    print c2
                    dirty = False # not really! But is a problem. 
                else:
                    dirty = False
            else:
                loc2 = c2.find("/>",loc)
                c2 = c2[:loc] + c2[loc2+2 :]
        c1 = f1.readline()
        c2 = f2.readline()

    f1.close()
    f2.close()


def main():
    # pass the filestem as argument
    basename = sys.argv[1]
    print "Checking ",basename + "_split.xml and "+basename+"_annotated.xml"
    readfiles(basename)

if __name__ == "__main__":
    main()

