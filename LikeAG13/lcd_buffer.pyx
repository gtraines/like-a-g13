cimport cython
import cairo
from cpython.array cimport array
from cpython.buffer cimport PyObject_GetBuffer

cdef inline unsigned int _rgb_r(unsigned int pixel_value):
    #define RGB_R(x) ((x&0x00FF0000) >> 16)
    return pixel_value & 0x00FF0000 >> 16

cdef inline unsigned int _rgb_g(unsigned int pixel_value):
    #define RGB_G(x) ((x&0x0000FF00) >> 8)
    return pixel_value & 0x0000FF00 >> 8

cdef inline unsigned int _rgb_b(unsigned int pixel_value):
    #define RGB_B(x) ((x&0x000000FF) >> 0)
    return pixel_value & 0x000000FF >> 0

cdef write_disp_matrix(unsigned int width, unsigned int threshold, array* surface_buffer):
    # calling semantics:
    # self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, g13.LCD_WIDTH, g13.LCD_HEIGHT)
    # self.context = cairo.Context(self.surface)
    # surface_buffer = cairo.surface.get_data()

    cdef unsigned source_len = len(surface_buffer)
    cdef bytes destination_buffer

    cdef unsigned row = 0, col = 0
    cdef size_t max_iterations
    cdef unsigned threshold = 128
    cdef char threshold_byte = threshold

    cdef int pixel_index = 0
    cdef int pixel_value = 0
    cdef bint show_pixel = False
    cdef int lcd_idx = 0

    for pixel_index in range(source_len):
      pixel_value = surface_buffer[pixel_index]

      show_pixel = _rgb_r(pixel_value) > threshold or \
            _rgb_g(pixel_value) > threshold or \
            _rgb_b(pixel_value) > threshold

      lcd_idx = 32 + col + (row >> 3) * width

      if show_pixel:
        destination_buffer[lcd_idx] |= 1 << (row & 0x07)
      else:
        destination_buffer[lcd_idx] &= ~(1 << (row & 0x07))

      col += 1
      if col >= width:
        col = 0
        row +=1