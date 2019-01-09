    #define RGB_R(x) ((x&0x00FF0000) >> 16)
    #define RGB_G(x) ((x&0x0000FF00) >> 8)
    #define RGB_B(x) ((x&0x000000FF) >> 0)

    Py_buffer source_buffer;
    PyObject_GetBuffer(source, &source_buffer, PyBUF_WRITABLE);

    unsigned int* source_buf = (unsigned int*)source_buffer.buf;
    int source_len = source_buffer.len;

    char* dest_buf = PyByteArray_AsString(dest);

    int row = 0, col = 0;
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