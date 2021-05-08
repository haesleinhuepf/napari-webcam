"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
import time

from napari._qt.qthreading import thread_worker
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpinBox, QCheckBox, QGridLayout, QLabel
from magicgui import magic_factory
import cv2
from ._function import acquire

class ContinuousAcquisition(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.btn = QPushButton("Start Acquisition")
        self.btn.clicked.connect(self._on_click)

        self.camera_index_spinner = QSpinBox()

        self.rgb_checkbox = QCheckBox()

        self.setLayout(QGridLayout(self))
        self.layout().addWidget(QLabel("Camera"), 0, 0)
        self.layout().addWidget(self.camera_index_spinner, 0, 1)
        self.layout().addWidget(QLabel("RGB"), 1, 0)
        self.layout().addWidget(self.rgb_checkbox, 1, 1)
        self.layout().addWidget(self.btn, 2, 1)
        #self.layout().addStretch()

        self.image_layer = None
        self.camera_device = None
        self.worker = None
        self.acquisition_count = 0

    def _on_click(self):

        if self.camera_device:
            # stop imaging
            self.camera_device.release()
            self.camera_device = None
            self.btn.setText("Start Acquisition")
            return
        else:
            # start imaging
            self.acquisition_count += 1
            self.camera_device = cv2.VideoCapture(self.camera_index_spinner.value())
            self.btn.setText("Stop Acquisition")

            # Multi-threaded interaction
            # inspired by https://napari.org/docs/dev/events/threading.html
            def update_layer(data):
                for name, image in data.items():
                    if image is not None:
                        try:
                            # replace layer if it exists already
                            self.viewer.layers[name].data = image
                        except KeyError:
                            # add layer if not
                            self.viewer.add_image(
                                image, name=name, blending='additive'
                            )

            @thread_worker
            def yield_acquire_images_forever():
                while True:  # infinite loop!
                    if self.camera_device:
                        yield {'image' + str(self.acquisition_count): acquire(keep_connection=True, device=self.camera_device, rgb=self.rgb_checkbox.isChecked())}
                    time.sleep(0.05)

            # Start the imaging loop
            if self.worker is None:
                self.worker = yield_acquire_images_forever()
                self.worker.yielded.connect(update_layer)
                self.worker.start()

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [ContinuousAcquisition]
