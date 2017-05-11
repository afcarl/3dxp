import glob
import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import biggest
from scripts import deepest


def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    BLOCK = args['block']
    TRIAL = args['trial']
    TOP_DEEP = args['deep']
    N_TOP_IDS = args['number'] + 1
    DATA = realpath(args['ids'])
    ROOTOUT = realpath(args['out'])
    STLFOLDER = sharepath(ROOTOUT, 'stl')

    #
    # IF A LIST OF IDS IS PASSED
    #
    if args['list'] != '':
        LIST = [int(v) for v in args['list'].split(':')]

        print args['list']

        # Load ids and make stl files
        if os.path.exists(DATA):

            with h5py.File(DATA, 'r') as df:
                vol = df[df.keys()[0]]
                full_shape = np.array(vol.shape)
                # Get number of blocks and block size
                block_size = np.uint32(np.ceil(full_shape/BLOCK))
                ntiles = np.uint32([BLOCK]*3)


        # Get all possible tile offsets
        subvols = zip(*np.where(np.ones(ntiles)))

        z,y,x = subvols[TRIAL]

        ThreeD.run(DATA, z, y, x, STLFOLDER, block_size, LIST)

        print('All done with stl block {},{},{}'.format(z,y,x))

        return




    # Count the biggest and the deepest ids 
    BIG_IDS, BIG_COUNTS = biggest(DATA, sharepath(ROOTOUT, 'spread_count.txt'), BLOCK)
    DEEP_IDS, DEEP_COUNTS = deepest(DATA, sharepath(ROOTOUT, 'deep_count.txt'), BLOCK)
    # Get the id numbers to use to generate meshes
    top_ids = [BIG_IDS, DEEP_IDS][TOP_DEEP][-N_TOP_IDS:-1]
    # No matter what, get the total block counts for each ID
    big_ids = [np.where(BIG_IDS == tid)[0][0] for tid in top_ids]
    top_counts = BIG_COUNTS[big_ids]

    # Load ids and make stl files
    if os.path.exists(DATA):

        with h5py.File(DATA, 'r') as df:
            vol = df[df.keys()[0]]
            full_shape = np.array(vol.shape)
            # Get number of blocks and block size
            block_size = np.uint32(np.ceil(full_shape/BLOCK))
            ntiles = np.uint32([BLOCK]*3)

        # Get all possible tile offsets
        subvols = zip(*np.where(np.ones(ntiles)))

        # Only search volume for ids that need more stl files
        re_path = [os.path.join(STLFOLDER,str(intid)+'_*') for intid in top_ids]

        z,y,x = subvols[TRIAL]
        # Check for existing stl files
        found_counts = [len(glob.glob(re_file)) for re_file in re_path]
        top_stl_ids = top_ids[top_counts>found_counts]
        if len(top_stl_ids):
            ThreeD.run(DATA, z, y, x, STLFOLDER, block_size, top_stl_ids)

        print('All done with stl block {},{},{}'.format(z,y,x))

def parseArgv(argv):
    sys.argv = argv

    help = {
        'ids': 'input hd5 id volume (default in.h5)',
        'out': 'output web directory (default .)',
        'd': 'rank top ids by depth (default 0)',
        'b': 'Number of blocks in each dimension (default 10)',
        't': 'Which of the b*b*b tiles to generate (default 0)',
        'n': 'make meshes for the top n ids (default 1)',
        'l': 'make meshes for : separated list of ids',
        'help': 'Make an hdf5 file into stl meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('ids', help=help['ids'])
    parser.add_argument('out', help=help['out'])
    parser.add_argument('-d','--deep',type=int, default=0, help=help['d'])
    parser.add_argument('-t','--trial', type=int, default=0, help=help['t'])
    parser.add_argument('-b','--block', type=int, default=10, help=help['b'])
    parser.add_argument('-n','--number', type=int, default=1, help=help['n'])
    parser.add_argument('-l','--list', default='', help=help['l'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

