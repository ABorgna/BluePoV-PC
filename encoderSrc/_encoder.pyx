""" C function wrapper for encoder.c """

# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

# if you want to use the Numpy-C-API from Cython
# (not strictly necessary for this example)
np.import_array()

# cdefine the signature of our c function
cdef extern from "encoder.h":
    void encodeRGB3d_C(unsigned char * in_array, unsigned char * out_array,
                       int height, int size, int bits, int bitsDone)
    void encodeRGB3dI_C(unsigned char * in_array, unsigned char * out_array,
                        int height, int size, int bits, int bitsDone)

# create the wrapper code, with numpy type annotations
def encodeRGB3d(np.ndarray[unsigned char, ndim=1, mode="c"] in_array not None,
                np.ndarray[unsigned char, ndim=1, mode="c"] out_array not None,
                int bits,
                int height):
    encodeRGB3d_C(<unsigned char*> np.PyArray_DATA(in_array),
           <unsigned char*> np.PyArray_DATA(out_array),
           height,
           in_array.shape[0],
           bits,
           0)

def encodeRGB3dI(np.ndarray[unsigned char, ndim=1, mode="c"] in_array not None,
                np.ndarray[unsigned char, ndim=1, mode="c"] out_array not None,
                int bits,
                int height):
    encodeRGB3dI_C(<unsigned char*> np.PyArray_DATA(in_array),
           <unsigned char*> np.PyArray_DATA(out_array),
           height,
           in_array.shape[0],
           bits,
           0)
