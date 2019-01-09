    #define RGB_R(x) ((x&0x00FF0000) >> 16)
    #define RGB_G(x) ((x&0x0000FF00) >> 8)
    #define RGB_B(x) ((x&0x000000FF) >> 0)

cimport cython
import cairocffi as cairo

def write_disp_matrix(int width, int threshold, char* surface_buffer):

    cdef char* dest_buf;
    cdef int row = 0, col = 0
    cdef size_t max_iterations
    for  in thresh:

    for (int pi=0; pi < source_len / 4; pi++) {
      int pix = source_buf[pi];
      bool pixel = RGB_R(pix) > %(threshold)s ||
                   RGB_G(pix) > %(threshold)s ||
                   RGB_B(pix) > %(threshold)s;
      int idx = 32 + col + (row >> 3) * %(width)s;
      if (pixel)
        dest_buf[idx] |= 1 << (row & 0x07);
      else
        dest_buf[idx] &= ~(1 << (row & 0x07));

      col++;
      if (col >= %(width)s) {
        col = 0;
        row++;
      }
    }