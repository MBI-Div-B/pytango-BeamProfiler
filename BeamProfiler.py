#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 16:04:50 2021

@author: moke
"""

from tango import  AttrWriteType, DevState,  DevFloat, DeviceProxy, DebugIt
from tango.server import Device, attribute, device_property
import numpy as np
import lmfit as lm


class BeamProfiler(Device):
    '''
    Beam profiler
    This device can measure the FWHM of any incoming signal. It grabs the data
    from an image and does a gaussian fitting both in x and y axis of the image.
    
    This device returns the FWHM both in x and y axis in micrometer. Take into 
    account that in order to be able to read the value FWHM, first you 
    should click on both data_x and data_y tabs so that the device knows which 
    the length of the data in both axis.
    
    To select which is the camera one wants to use, you must write 
    in dev_properties from the Basler device in Jive, the serial number of 
    the desired camera, which is usually written on the camera as S/N).
    
    ****** In case the camera is changed, the propertie resolution
    is a parameter that needs to be checked because it may be different for 
    each camera brand. Basler cameras acA1300 - 60gm have a resolution of
    5.3 micrometer/pixel.
    
    '''   
    data_x = attribute(name='data_x', label='data x',max_dim_x=4096,
                      dtype=(DevFloat,), access=AttrWriteType.READ)
    data_y = attribute(name='data_y', label='data y',max_dim_x=4096,
                      dtype=(DevFloat,), access=AttrWriteType.READ)
    
    from_x = attribute(label='from x (select pixel position)', dtype="float", 
                        access=AttrWriteType.READ_WRITE, memorized=True, 
                        hw_memorized=False)

    to_x = attribute(label='to x', dtype="float", 
                        access=AttrWriteType.READ_WRITE, memorized=True, 
                        hw_memorized=False)
    
    from_y = attribute(label='from y', dtype="float", 
                        access=AttrWriteType.READ_WRITE, memorized=True, 
                        hw_memorized=False)
    to_y = attribute(label='to y', dtype="float", 
                        access=AttrWriteType.READ_WRITE, memorized=True, 
                        hw_memorized=False)
    
    
    fitting_x = attribute(name='fitting_x', label='fitting x',max_dim_x=4096,
                      dtype=(DevFloat,), access=AttrWriteType.READ)
    fitting_y = attribute(name='fitting_y', label='fitting y',max_dim_x=4096,
                      dtype=(DevFloat,), access=AttrWriteType.READ)
    
    width_x = attribute(label='FWHM x (micrometer)', 
                            dtype="float",format="%4.3f", access=AttrWriteType.READ)
    width_y = attribute(label='FWHM y (micrometer)', dtype="float",
                         format="%4.3f", access=AttrWriteType.READ)

    __minimum_y = 0
    __minimum_x = 0
    resolution = device_property(dtype="float") # micrometer/ 1 pixel for Basler camera
    
    sigma_try = 33.15
    
    def init_device(self):
        self.debug_stream("Preparing device")
        Device.init_device(self)
        try:
            self.camera = DeviceProxy('MOKE/Basler/autocorrelator')
            self.debug_stream('Init was done')
        except:
            self.error_stream('Could not contact camera :( ')
            self.set_state(DevState.OFF)
        self.set_state(DevState.ON)
        
    def read_data_x(self):
        self.debug_stream("Graphing x axis")
        real_data = self.camera.image
        self.N = len(real_data[0,:])
        self.__maximum_x = self.N
        self.x_axis = np.mean(real_data, axis = 0)
        self.debug_stream('cameras x axis was graphed properly')
        return self.x_axis
    
    def read_data_y(self):
        self.debug_stream("Graphing y axis")
        real_data = self.camera.image
        self.N2 = len(real_data[:,0])
        self.__maximum_y = self.N2
        self.y_axis = np.mean(real_data[self.__minimum_y:self.__maximum_y], axis = 1)
        self.debug_stream('cameras y axis was graphed properly')
        return self.y_axis
    
    
    def read_from_y(self):
        return self.__minimum_y
    
    def write_from_y(self, value):
        self.__minimum_y = value
        
    def read_from_x(self):
        return self.__minimum_x
    
    def write_from_x(self, value):
        self.__minimum_x = value
        
        
        
    def read_to_x(self):
        return self.__maximum_x
    
    def write_to_x(self, value):
        self.__maximum_x = value
        
    def read_to_y(self):
        return self.__maximum_y
    
    def write_to_y(self, value):
        self.__maximum_y = value
        

    
    def read_width_x(self):
        self.debug_stream('trying to calculate de width x') 
        real_data = self.camera.image
        self.x_axis = np.mean(real_data, axis = 0)
        self.debug_stream('getting data x') 
        self.__maximum_x = int(self.__maximum_x)
    
        self.__minimum_x = int(self.__minimum_x)
        aa = self.__minimum_x
        bb = self.__maximum_x
        self.x_axis = self.x_axis[aa:bb]
        
        self.debug_stream('redefining limits in x') 
        self.x = np.linspace(aa,bb,len(self.x_axis))

        self.debug_stream('ordinates image axis') 
        def gaussian_paula(x, mu, A, sigma, c):
            return A*np.exp(-(x-mu)**2/(2*sigma**2))+c
        
        self.mod = lm.Model(gaussian_paula)
        self.pars = lm.Parameters()
        
        self.x_max = np.max(self.x_axis)
        self.x_min = np.min(self.x_axis)
        self.muu = self.x_axis.argmax()
        self.pars.add('mu', value = self.muu)
        self.pars.add('A', value = self.x_max-self.x_min)
        self.pars.add('c', value = self.x_min)
        self.pars.add('sigma', value = self.sigma_try )
        self.out_x = self.mod.fit(self.x_axis, self.pars, x=self.x) 
        self.debug_stream('parameters & fitting x axis data successful') 
        return 2*np.sqrt(2*np.log(2))*self.out_x.best_values['sigma']*self.resolution
    
    
    def read_width_y(self):
        self.debug_stream('trying to calculate de width y') 
        real_data = self.camera.image
        y_axis = np.mean(real_data, axis = 1)
        
        self.__maximum_y = int(self.__maximum_y)
    
        self.__minimum_y = int(self.__minimum_y)
        cc = self.__minimum_y
        dd = self.__maximum_y
        
        self.y_axis = y_axis[cc:dd]
    
        self.y = np.linspace(cc,dd,len(self.y_axis))
        
        def gaussian_paula(x, mu, A, sigma, c):
            return A*np.exp(-(x-mu)**2/(2*sigma**2))+c
        
        self.mod = lm.Model(gaussian_paula)
        self.pars = lm.Parameters()
        
        self.y_max = np.max(self.y_axis)
        self.y_min = np.min(self.y_axis)
        self.muu = self.y_axis.argmax()
        self.pars.add('mu', value = self.muu)
        self.pars.add('A', value = self.y_max-self.y_min)
        self.pars.add('c', value = self.y_min)
        self.pars.add('sigma', value = self.sigma_try )
        self.out_y = self.mod.fit(self.y_axis, self.pars, x=self.y) 
        self.debug_stream('parameters & fitting y axis data successful') 
        return 2*np.sqrt(2*np.log(2))*self.out_y.best_values['sigma']*self.resolution
    
    def read_fitting_x(self):
        return self.out_x.best_fit
    
    def read_fitting_y(self):
        return self.out_y.best_fit
    
if __name__ == "__main__":
    BeamProfiler.run_server()
