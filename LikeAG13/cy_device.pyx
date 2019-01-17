from hid cimport chid
import usb1

print(dir(chid))
"""
from libc.stddef cimport wchar_t, size_t

cdef extern from "hidapi.h":
  ctypedef struct hid_device:
    pass

  cdef struct hid_device_info:
    char *path
    unsigned short vendor_id
    unsigned short product_id
    wchar_t *serial_number
    unsigned short release_number
    wchar_t *manufacturer_string
    wchar_t *product_string
    unsigned short usage_page
    unsigned short usage
    int interface_number
    hid_device_info *next

  hid_device_info* hid_enumerate(unsigned short, unsigned short)
  void hid_free_enumeration(hid_device_info*)
  int hid_exit()

  hid_device* hid_open(unsigned short, unsigned short, const wchar_t*)
  hid_device* hid_open_path(char *path)
  void hid_close(hid_device *)
  int hid_write(hid_device* device, unsigned char *data, int length) nogil
  int hid_read(hid_device* device, unsigned char* data, int max_length) nogil
  int hid_read_timeout(hid_device* device, unsigned char* data, int max_length, int milliseconds) nogil
  int hid_set_nonblocking(hid_device* device, int value)
  int hid_send_feature_report(hid_device* device, unsigned char *data, int length) nogil
  int hid_get_feature_report(hid_device* device, unsigned char *data, int length) nogil

  int hid_get_manufacturer_string(hid_device*, wchar_t *, size_t)
  int hid_get_product_string(hid_device*, wchar_t *, size_t)
  int hid_get_serial_number_string(hid_device*, wchar_t *, size_t)
  wchar_t *hid_error(hid_device *)
"""

DEF VENDOR_ID = 0x046d
DEF PRODUCT_ID = 0xc21c
DEF INTERFACE = 0
DEF MODE_LED_CONTROL = 0x301  # Could be 0x302?
DEF COLOR_CONTROL = 0x301  # Could be 0x307? Graham: Nope, so far just 0x301
DEF KEY_ENDPOINT = 1
DEF REPORT_SIZE = 8
DEF LCD_WIDTH = 160
DEF LCD_HEIGHT = 43

# Arguments and return types of cpdef funcs must be Py objects, meaning NO POINTER types
cdef class CyDevice:
    cdef readonly:
        unsigned int REQUEST_TYPE = usb1.REQUEST_TYPE_CLASS | usb1.RECIPIENT_INTERFACE
    cdef:
        chid.hid_device_info* _g13_handle
        chid.hid_device* _g13_device

    def __cinit__(self):
        self._g13_handle = sizeof(chid.hid_device_info)

    cpdef void open(self):
        self._g13_handle = chid.hid_enumerate(VENDOR_ID, PRODUCT_ID)
        if self._g13_handle is not NULL:
            print(self._g13_handle.vendor_id)





