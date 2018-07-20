"""
### BEGIN EXPERIMENT INFO
[info]
name = ion_position_tracker
load_into_scriptscanner = True
allow_concurrent = []
### END EXPERIMENT INFO
"""

import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import time
import numpy as np
from skimage.feature import blob_dog

class ion_position_tracker(QsimExperiment):

    name = 'ion_position_tracker'

    exp_parameters = []

    exp_parameters.append(('images', 'image_center_x'))
    exp_parameters.append(('images', 'image_center_y'))
    exp_parameters.append(('images', 'image_width'))
    exp_parameters.append(('images', 'image_height'))
    exp_parameters.append(('images', 'measure_time'))
    exp_parameters.append(('images', 'blob_detect_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cam = cxn.andor_server
        self.exposure = self.cam.get_exposure_time
        self.grapher = cxn.grapher


    def run(self, cxn, context):
        elapsed = WithUnit(0.0, 's')
        self.dv.cd(['','Ion Location Tracker'],True)
        self.dataset = self.dv.new('ion position', [('Time', 's')], [('X Location','X Location','um'), ('Y Location','Y Location','um'), ('Ion Diameter','Ion Diameter', 'um')])
        self.grapher.plot(self.dataset, 'Ion Drift Tracker', False)
        self.set_scannable_parameters()
        self.set_exp_settings()
        init_time = time.time()
        while elapsed <= self.p.images.measure_time:
            data = np.reshape(self.cam.get_most_recent_image(), (self.image_y_length, self.image_x_length))
            ion = blob_dog(data, max_sigma = 10, sigma_ratio = 1.6, threshold = self.p.images.blob_detect_threshold)
            xPos, yPos, diameter = WithUnit(ion[0][0]/7.7, 'um'), WithUnit(ion[0][1]/7.7, 'um'), WithUnit(ion[0][2]*np.sqrt(2)*2/7.7, 'um')
            elapsed = WithUnit(time.time() - init_time, 's')
            self.dv.add([elapsed['s'], xPos['um'], yPos['um'], diameter['um']])
            should_break = self.update_progress(elapsed['s']/self.p.images.measure_time['s'])
            if should_break:
                break

    def set_exp_settings(self):

        self.cam.abort_acquisition()
        self.cam.set_image_region(
            [1, 1, self.y_pixel_range[0], self.y_pixel_range[1], self.x_pixel_range[0], self.x_pixel_range[1]])
        self.cam.start_live_display()

    def set_scannable_parameters(self):
        center_y = self.p.images.image_center_x['pix'] #  switched for same reason
        center_x = self.p.images.image_center_y['pix']
        height = self.p.images.image_width['pix']
        width = self.p.images.image_height['pix']  # switched due to transpose of camera data
        self.x_pixel_range = [int(center_x - width/2), int(center_x + width/2)] # rounds image size
        self.y_pixel_range = [int(center_y - height/2), int(center_y + height/2)]
        self.image_x_length = self.x_pixel_range[-1] - self.x_pixel_range[0] + 1
        self.image_y_length = self.y_pixel_range[-1] - self.y_pixel_range[0] + 1
        self.data_size = [self.image_x_length, self.image_y_length]

    def finalize(self, cxn, context):
        hor_max, ver_max = self.cam.get_detector_dimensions(None)
        hor_min, ver_min = [1, 1]
        self.cam.abort_acquisition()
        self.cam.set_image_region([1, 1, hor_min, hor_max, ver_min, ver_max])
        self.cam.start_live_display()
        
    
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ion_position_tracker(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
