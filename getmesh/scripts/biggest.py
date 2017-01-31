import sys, argparse
from toArgv import toArgv
import numpy as np
import os, h5py

def sort(counts):
    keysort = np.argsort(counts).astype(np.uint32)
    return [keysort, counts[keysort]]

def start(_argv):
    args = parseArgv(_argv)

    DATA = args['hd5']
    TILESIZE = args['s']
    COUNTPATH = args['out']
    COUNTS = []

    if os.path.exists(COUNTPATH):
        COUNTS = np.loadtxt(COUNTPATH,dtype=np.uint32)
        return sort(COUNTS)

    with h5py.File(DATA, 'r') as df:
        vol = df[df.keys()[0]]
        sizes = vol.shape
        ntiles = np.array(sizes)//TILESIZE

        subvols = zip(*np.where(np.ones(ntiles)))
        z_base = 1./ntiles[0]
        y_base = z_base/ntiles[1]
        x_base = y_base/ntiles[2]

        for z,y,x in subvols:

            zo,ze = np.array([z,z+1])*TILESIZE
            yo,ye = np.array([y,y+1])*TILESIZE
            xo,xe = np.array([x,x+1])*TILESIZE
            in_block = np.unique(vol[zo:ze, yo:ye, xo:xe])

            new_count = np.zeros(max(in_block)+1)
            new_count[in_block] = 1
            diff_count = len(new_count) - len(COUNTS)
            if diff_count > 0:
                COUNTS = np.r_[COUNTS, np.zeros(diff_count)]
            if diff_count < 0:
                new_count = np.r_[new_count, np.zeros(-diff_count)]

            COUNTS = COUNTS + new_count

            z_done = z*z_base + y*y_base + x*x_base
            print("%.1f%% done with counting" % (100*z_done) )

        np.savetxt(COUNTPATH, COUNTS, fmt='%i')
        return sort(COUNTS)

def parseArgv(argv):
    sys.argv = argv

    help = {
        's': 'load h5 in s*s*s chunks (default 256)',
        'out': 'output count text file (defalt spread_count.txt)',
        'hd5': 'input segmentation hd5 file (default in.h5)',
        'help': 'Find biggest IDs in segmented volume'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('hd5', default='in.h5', nargs='?', help=help['hd5'])
    parser.add_argument('out', default='spread_count.txt', nargs='?', help=help['out'])
    parser.add_argument('-s', type=int, default=256, help=help['s'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)

