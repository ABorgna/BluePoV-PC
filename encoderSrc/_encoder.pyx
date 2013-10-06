""" C function wrapper for encoder.c """

# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

# if you want to use the Numpy-C-API from Cython
# (not strictly necessary for this example)
np.import_array()

# cdefine the signature of our c function
cdef extern from "encoder.h":
    void encode (unsigned char * in_array, unsigned char * out_array, int size)

# create the wrapper code, with numpy type annotations
def encode_func(np.ndarray[unsigned char, ndim=1, mode="c"] in_array not None,
                np.ndarray[unsigned char, ndim=1, mode="c"] out_array not None):
    encode(<unsigned char*> np.PyArray_DATA(in_array),
           <unsigned char*> np.PyArray_DATA(out_array),
           in_array.shape[0])
