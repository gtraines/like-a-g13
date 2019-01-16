import collections
import platform
import usb1
from usb1 import USBError

G13_KEY_BYTES = collections.namedtuple('G13_KEY_BYTES', [
    'stick_x', 'stick_y', 'keys'])

KeyPress = collections.namedtuple('KeyPress', ['key_name', 'is_pressed'])
NamedColor = collections.namedtuple('NamedColor', [
    'name', 'red_value', 'green_value', 'blue_value'])

G13_KEYS = [  # Which bit should be set
    # /* byte 3 */
    'G01',
    'G02',
    'G03',
    'G04',

    'G05',
    'G06',
    'G07',
    'G08',

    # /* byte 4 */
    'G09',
    'G10',
    'G11',
    'G12',

    'G13',
    'G14',
    'G15',
    'G16',

    # /* byte 5 */
    'G17',
    'G18',
    'G19',
    'G20',

    'G21',
    'G22',
    'UN1',  # 'UNDEF1',
    'LST',  # 'LIGHT_STATE',

    # /* byte 6 */
    'BD',
    'L1',
    'L2',
    'L3',

    'L4',
    'M1',
    'M2',
    'M3',

    # /* byte 7 */
    'MR',
    'LFT',
    'DWN',
    'TOP',

    'UN2',  # 'UNDEF2',
    'LT1',  # 'LIGHT',
    'LT2',  # 'LIGHT2',
    # 'MISC_TOGGLE',
]


class LedColors(object):
    PINK = NamedColor('pink', 100, 100, 100)
    FUSCHIA = NamedColor('fuschia', 255, 100, 255)
    PURPLE = NamedColor('purple', 128, 0, 128)
    RED = NamedColor('red', 255, 0, 0)
    MAROON = NamedColor('maroon', 128, 0, 0)
    YELLOW = NamedColor('yellow', 250, 250, 0)
    GREEN = NamedColor('green', 5, 200, 5)
    LIME = NamedColor('lime', 0, 255, 0)
    AQUA = NamedColor('aqua', 0, 255, 255)
    BLUE = NamedColor('blue', 0, 128, 255)


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
            return self.device
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
        if self.device_handle is not None:
            self.device_handle.releaseInterface(self.INTERFACE)
            self.device_handle.close()
        if self.device_context is not None:
            self.device_context.exit()

    def get_key_press_bytes(self):
        try:
            data = None
            try:
                data = self.device_handle.interruptRead(
                    endpoint=self.KEY_ENDPOINT, length=self.REPORT_SIZE, timeout=500)
            except USBError as usb_ex:
                if usb_ex.value == -7:
                    pass
            if data is not None:
                keys = list(map(ord, data))
                keys[7] &= ~0x80  # knock out a floating-value key
                return G13_KEY_BYTES(keys[1], keys[2], keys[3:])
            return None
        except Exception as ex:
            print(ex)
            self.close()
            raise ex

    def parse_keys(self):
        keys = self.get_key_press_bytes()
        if not any(keys.keys):
            return None
        key_press_bit_map = []
        for i, key in enumerate(G13_KEYS):
            b = keys.keys[int(i / 8)]
            key_press_bit_map.append(KeyPress(key, b & 1 << (i % 8)))
        return key_press_bit_map

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
