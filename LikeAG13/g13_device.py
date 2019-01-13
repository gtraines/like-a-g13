import collections
import platform
import usb1

G13_KEY_BYTES = collections.namedtuple('G13_KEY_BYTES', [
    'stick_x', 'stick_y', 'keys'])

NamedColor = collections.namedtuple('NamedColor', [
    'name', 'red_value', 'green_value', 'blue_value'])


class LedColors(object):
    FUSCHIA = NamedColor('fuschia', 100, 100, 100)


class MissingG13Error(Exception):
    """No G13 found on USB."""


class G13Device(object):
    VENDOR_ID = 0x046d
    PRODUCT_ID = 0xc21c
    INTERFACE = 0
    MODE_LED_CONTROL = 0x301  # Could be 0x302?
    COLOR_CONTROL = 0x301  # Could be 0x307? Graham: Nope, so far just 0x301
    KEY_ENDPOINT = 1
    REPORT_SIZE = 8
    REQUEST_TYPE = usb1.REQUEST_TYPE_CLASS | usb1.RECIPIENT_INTERFACE

    LCD_WIDTH = 160
    LCD_HEIGHT = 43

    def __init__(self):
        # 160 across and 43 down (6 bytes down)
        self.pixels = self.get_new_buffer()
        self.device = None
        self.device_handle = None
        self.device_context = None
        self.open()

    def open(self):
        try:
            self.device = self._try_obtain_device()
            self._try_obtain_device_handle()
        except IOError as io_ex:
            raise io_ex  # nothing we can do to recover from this
        except usb1.USBError as ex:
            if self.device is not None and self.device_handle is not None:
                self.device_handle.resetDevice()
                self._try_obtain_device_handle()

        # interruptRead -> R
        # controlWrite -> Out

    def _try_obtain_device(self):
        try:
            self.device_context = usb1.USBContext()
            self.device = self.device_context.getByVendorIDAndProductID(self.VENDOR_ID, self.PRODUCT_ID)

            if self.device is None:
                raise MissingG13Error()
        except MissingG13Error as missing_ex:
            raise missing_ex
        except Exception as ex:
            print(ex)
            raise IOError(ex, "Did you run utils/set_perms.sh?")

    def _try_obtain_device_handle(self):

        try:
            self.device_handle = self.device.open()

        except Exception as ex:
            raise IOError(ex, "Did you run utils/set_perms.sh?")

        if platform.system() == 'Linux' and \
                self.device_handle.kernelDriverActive(self.INTERFACE):
            self.device_handle.detachKernelDriver(self.INTERFACE)

        self.device_handle.claimInterface(self.INTERFACE)

    def close(self):
        self.device_handle.releaseInterface(self.INTERFACE)
        self.device_handle.close()
        self.device_context.exit()

    def get_keys(self):
        try:
            data = self.device_handle.interruptRead(
                endpoint=self.KEY_ENDPOINT, length=self.REPORT_SIZE, timeout=100)
            keys = list(map(ord, data))
            keys[7] &= ~0x80  # knock out a floating-value key
            return G13_KEY_BYTES(keys[1], keys[2], keys[3:])
        except Exception as ex:
            self.close()

    def set_led_mode(self, mode):
        try:
            data = ''.join(map(chr, [5, mode, 0, 0, 0]))
            self.device_handle.controlWrite(
                request_type=self.REQUEST_TYPE, request=9,
                value=self.MODE_LED_CONTROL, index=0, data=data.encode(),
                timeout=1000)
        except Exception as ex:
            self.close()

    def set_color(self, color):
        self.set_color_from_rgb(color[0], color[1], color[2])

    def set_color_from_named_color(self, named_color):
        self.set_color_from_rgb(named_color[1], named_color[2], named_color[3])

    def set_color_from_rgb(self, red_value, green_value, blue_value):
        try:
            data = ''.join(map(chr, [7, red_value, green_value, blue_value, 0]))
            self.device_handle.controlWrite(
                request_type=self.REQUEST_TYPE, request=9,
                value=self.COLOR_CONTROL, index=0, data=data.encode(),
                timeout=1000)
        except Exception as ex:
            self.close()

    @staticmethod
    def get_new_buffer():
        new_buffer = bytearray(992)
        new_buffer[0] = 3
        return new_buffer

    def update_lcd_from_pixels(self):
        try:
            self.device_handle.interruptWrite(endpoint=2, data=memoryview(self.pixels).tobytes(), timeout=1000)
        except Exception as ex:
            self.close()

    def update_lcd_from_buffer(self, bytesarray_buffer):
        self.pixels = bytesarray_buffer
        self.update_lcd_from_pixels()

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