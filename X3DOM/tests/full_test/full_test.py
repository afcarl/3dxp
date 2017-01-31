import sys
import getmesh

if __name__ == "__main__":
    flags = {
        #'size': 256,
        #'index': 'index.html',
        'www': '../../www',
        'number': int(sys.argv[1]),
        'root': '~/2017/data/seg_100x4x4',
        'deep': 1
    }
    inpaths = ['stitched_seg.h5', 'grayscale.h5', 'grayscale_maps_converted']
    getmesh.main(*inpaths, **flags)