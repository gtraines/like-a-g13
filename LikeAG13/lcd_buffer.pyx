cimport cython
import cairo

cdef inline _rgb_r(unsigned int pixel_value):
    #define RGB_R(x) ((x&0x00FF0000) >> 16)
    return pixel_value & 0x00FF0000 >> 16

cdef inline _rgb_g(unsigned int pixel_value):
    #define RGB_G(x) ((x&0x0000FF00) >> 8)
    return pixel_value & 0x0000FF00 >> 8

cdef inline _rgb_b(unsigned int pixel_value):
    #define RGB_B(x) ((x&0x000000FF) >> 0)
    return pixel_value & 0x000000FF >> 0

cdef write_disp_matrix(int width, int threshold, char* surface_buffer):

    cdef char* dest_buf
    cdef int row = 0, col = 0
    cdef size_t max_iterations
    cdef int threshold = 128
    cdef char threshold_byte = threshold

    cdef int source_len = 1024
    cdef int pixel_index = 0
    cdef int pixel_value = 0
    cdef bool show_pixel = False
    cdef int lcd_idx = 0

    for pixel_index in range(source_len):
      pixel_value = surface_buffer[pixel_index]

      show_pixel = _rgb_r(pixel_value) > threshold or \
            _rgb_g(pixel_value) > threshold or \
            _rgb_b(pixel_value) > threshold

      lcd_idx = 32 + col + (row >> 3) * width

      if show_pixel:
        dest_buf[lcd_idx] |= 1 << (row & 0x07)
      else:
        dest_buf[lcd_idx] &= ~(1 << (row & 0x07))

      col += 1
      if col >= width:
        col = 0
        row +=1