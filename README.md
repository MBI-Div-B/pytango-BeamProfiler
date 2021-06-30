# pyTango-BeamProfiler

PyTango Device Server for calculating FWHM of a laser beam profile [µm] in two directions.

Right now is only integrating in the horizontal and vertical axis. As the fitting is performed in a Gaussian shape, it is possible to choose a diferent integration axis by choosing an angle theta. I tried to implement this however I didn't succeed but it is commented in the code in case someone wants to try it again in the future.
