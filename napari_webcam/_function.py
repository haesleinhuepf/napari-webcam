from enum import Enum
import numpy as np
from cv2.cv2 import VideoCapture
from napari.types import ImageData, LayerDataTuple
from napari_plugin_engine import napari_hook_implementation


def acquire(camera_index=0, keep_connection=False, rgb=False, device : VideoCapture = None):
    """
    Acquires an image from the computer's webcam and returns it.
    If the computer has multiple cameras, you can specify the index as parameter.

    Parameters
    ----------
    camera_index: int
        zero based camera inde
    keep_connection: bool
        if true, the connection will be kept open making the next acquisition faster
    rgb : bool
        return an RGB image if true, single channel grey scale otherwise
    device : VideoCapture
        an acquisition device, optional

    Returns
    -------
        2d (single channel) or 3d (RGB) numpy array / image
    """
    import cv2

    if device is None:
        if not hasattr(acquire, "video_source"):
            acquire.video_source = cv2.VideoCapture(camera_index)
        device = acquire.video_source

    _, picture = device.read()
    if picture is None:
        return

    if not keep_connection:
        device.release()
        del acquire.video_source

    if rgb:
        picture[:,:,0], picture[:,:,2] = picture[:,:,2], picture[:,:,0]
    else:
        from skimage.color import rgb2gray
        picture = rgb2gray(picture)

    return picture

@napari_hook_implementation
def napari_experimental_provide_function():
    return [acquire_image]

def acquire_image(camera_index: int = 0, rgb : bool = False) -> LayerDataTuple:
    """Acquire an image from a webcam"""

    picture = acquire(camera_index=camera_index, rgb=rgb)

    #if rgb:
    #    from skimage.color import rgb2gray
    #    picture = rgb2gray(picture)

    print("HELLO WORLD")
    print(picture.shape)

    return (picture, {"rgb":rgb})
