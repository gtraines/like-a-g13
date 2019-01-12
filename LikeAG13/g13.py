import collections
import platform

import usb1

G13_KEY_BYTES = collections.namedtuple('G13_KEY_BYTES', [
    'stick_x', 'stick_y', 'keys'])


class MissingG13Error(Exception):
    """No G13 found on USB."""


class G13(object):
    VENDOR_ID = 0x046d
    PRODUCT_ID = 0xc21c
    INTERFACE = 0
    MODE_LED_CONTROL = 0x301  # Could be 0x302?
    COLOR_CONTROL = 0x301  # Could be 0x307? Graham: Nope, so far just 0x301
    KEY_ENDPOINT = 1
    REPORT_SIZE = 8
    REQUEST_TYPE = usb1.REQUEST_TYPE_CLASS | usb1.RECIPIENT_INTERFACE

    LCD_WIDTH = 160
    LCD_HEIGHT = 44

    def __init__(self):
        # 160 across and 43 down (6 bytes down)
        self.pixels = bytearray(992)
        self.pixels[0] = 3
        self.device_handle = None
        self.device_context = None
        self.open()

    def open(self):
        self.device_context = usb1.USBContext()
        dev = self.device_context.getByVendorIDAndProductID(self.VENDOR_ID, self.PRODUCT_ID)
        if not dev:
            raise MissingG13Error()
        try:
            self.device_handle = dev.open()
            if platform.system() == 'Linux' and \
                    self.device_handle.kernelDriverActive(self.INTERFACE):
                self.device_handle.detachKernelDriver(self.INTERFACE)

            self.device_handle.claimInterface(self.INTERFACE)
        except Exception as ex:
            raise IOError(ex, "Did you run utils/set_perms.sh?")

        # interruptRead -> R
        # controlWrite -> Out

    def close(self):
        self.device_handle.releaseInterface(self.INTERFACE)
        self.device_handle.close()
        self.device_context.exit()

    def get_keys(self):
        data = self.device_handle.interruptRead(
            endpoint=self.KEY_ENDPOINT, length=self.REPORT_SIZE, timeout=100)
        keys = list(map(ord, data))
        keys[7] &= ~0x80  # knock out a floating-value key
        return G13_KEY_BYTES(keys[1], keys[2], keys[3:])

    def set_led_mode(self, mode):
        data = ''.join(map(chr, [5, mode, 0, 0, 0]))
        self.device_handle.controlWrite(
            request_type=self.REQUEST_TYPE, request=9,
            value=self.MODE_LED_CONTROL, index=0, data=data.encode(),
            timeout=1000)

    def set_color(self, color):
        data = ''.join(map(chr, [7, color[0], color[1], color[2], 0]))
        self.device_handle.controlWrite(
            request_type=self.REQUEST_TYPE, request=9,
            value=self.COLOR_CONTROL, index=0, data=data.encode(),
            timeout=1000)

    def update_lcd_from_pixels(self):
        self.device_handle.interruptWrite(endpoint=2, data=str(self.pixels), timeout=1000)

    def set_pixel(self, x, y, val):
        x = min(x, 159)
        y = min(y, 43)
        idx = 32 + x + (y / 8) * 160
        if val:
            self.pixels[int(idx)] |= 1 << (y % 8)
        else:
            self.pixels[int(idx)] &= ~(1 << (y % 8))

    def __del__(self):
        self.close()
