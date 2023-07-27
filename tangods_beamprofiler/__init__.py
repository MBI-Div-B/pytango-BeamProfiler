from .BeamProfiler import BeamProfiler


def main():
    import sys
    import tango.server

    args = ["BeamProfiler"] + sys.argv[1:]
    tango.server.run((BeamProfiler,), args=args)
