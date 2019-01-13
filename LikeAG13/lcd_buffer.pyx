cimport cython
from cpython.array cimport array


cdef inline unsigned int _rgb_r(unsigned int pixel_value):
    #define RGB_R(x) ((x&0x00FF0000) >> 16)
    return pixel_value & 0x00FF0000 >> 16

cdef inline unsigned int _rgb_g(unsigned int pixel_value):
    #define RGB_G(x) ((x&0x0000FF00) >> 8)
    return pixel_value & 0x0000FF00 >> 8

cdef inline unsigned int _rgb_b(unsigned int pixel_value):
    #define RGB_B(x) ((x&0x000000FF) >> 0)
    return pixel_value & 0x000000FF >> 0

cpdef bytearray write_disp_matrix(unsigned int width, unsigned int threshold, unsigned char[:] surface_buffer, bytearray destination_buffer):

    cdef unsigned int source_len = len(surface_buffer)
    cdef unsigned int destination_len = len(destination_buffer)

    cdef unsigned char[:] destination_mv = memoryview(destination_buffer)
    cdef unsigned int row = 0, col = 0

    cdef char threshold_byte = threshold

    cdef unsigned int pixel_index = 0
    cdef unsigned char pixel_value = 0
    cdef bint show_pixel = False
    cdef unsigned int lcd_idx = 0

    for pixel_index in range(source_len):
        if pixel_index % 4 == 0:

            pixel_value = surface_buffer[pixel_index]

            show_pixel = _rgb_r(pixel_value) > threshold or \
                _rgb_g(pixel_value) > threshold or \
                _rgb_b(pixel_value) > threshold

            lcd_idx = 32 + col + (row >> 3) * width
            if lcd_idx < destination_len:
                if show_pixel:
                    destination_mv[lcd_idx] |= 1 << (row & 0x07)
                else:
                    destination_mv[lcd_idx] &= ~(1 << (row & 0x07))
            col += 1
            if col >= width:
                col = 0
                row +=1

    return destination_buffer
