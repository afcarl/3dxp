from toArgv import toArgv
import sys, argparse
import os, cv2, h5py
import mahotas as mh
import numpy as np

def start(_args):
    args = parseArgv(_args)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'help': 'Interpolate keyframes into many frames'
    }

    parser = argparse.ArgumentParser(description=help['help'])

    return vars(parser.parse_args())

def main(_args, **_flags):
    start(toArgv(_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)

