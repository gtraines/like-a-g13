from __future__ import print_function

import datetime
import sys
import threading
import time

import usb1

from LikeAG13 import G13Lcd, MissingG13Error

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


class TerminalUI(object):
    BASE_X, BASE_Y = 0, 10
    scale_x, scale_y = 64, 32

    def __init__(self):
        self.prev_x, self.prev_y = 0, 0
        self.prev_keys = {k: 1 for k in G13_KEYS}

    def init_stick(self):
        self.reset()
        sys.stdout.write('-' * (self.scale_x + 2) + '\n')
        for l in range(self.scale_y):
            sys.stdout.write('|' + ' ' * self.scale_x + '|\n')
        sys.stdout.write('-' * (self.scale_x + 2) + '\n')

    def reset(self):
        self.goto(0, 0)

    def goto(self, x, y):
        sys.stdout.write('\033[%s;%sH' % (self.BASE_Y + y, self.BASE_X + x))

    def down(self, num):
        sys.stdout.write('\033[%sB' % num)

    def right(self, num):
        sys.stdout.write('\033[%sC' % num)

    def print_at(self, x, y, s):
        self.goto(x + 1, y + 1)
        sys.stdout.write(s)

    def flush(self):
        sys.stdout.flush()

    def print_stick(self, x, y):
        x /= 4
        y /= 8

        self.print_at(self.prev_x + 1, self.prev_y, ' ')
        self.print_at(x + 1, y, 'x')

        self.prev_x, self.prev_y = x, y

    def clear_keys(self):
        if not any(self.prev_keys.values()):
            return
        for i in range(5):
            self.print_at(0, self.scale_y + 1 + i, ' ' * (4 * 8))

    def set_key(self, key, value):
        if self.prev_keys[key] != value:
            idx = G13_KEYS.index(key)
            y = self.scale_y + 1 + idx / 8
            x = (idx % 8) * 4
            if value:
                out = key
            else:
                out = '    '
            self.print_at(x, y, out)

        self.prev_keys[key] = value


def try_get_g13():
    try:
        g13_instance = G13Lcd()
        return g13_instance
    except MissingG13Error:
        print('No G13 found.')
        sys.exit(1)


def lcd_only_ui():
    g13 = try_get_g13()

    g13.draw_image('x.png', scale=0.2, offset=(200, 0))

    start = time.time()

    try:
        while True:  # for i in range(300):
            g13.print_time()
            t = 1 / (time.time() - start)
            time.sleep(1 - (time.time() % 1))
            start = time.time()
            g13.set_led_mode(int(time.time() % 16))
            g13.set_color((255, 0, 0))
            time.sleep(0.1)
            g13.set_led_mode(int(time.time() % 16))
            g13.set_color((255, 255, 255))
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print('^C')
    finally:
        g13.close()
    return


def std_out_ui():
    g13 = try_get_g13()
    ui = TerminalUI()
    ui.init_stick()
    try:
        while True:
            try:
                keys = g13.get_keys()

                g13.print_stick(keys.stick_x, keys.stick_y)
                ui.print_stick(keys.stick_x, keys.stick_y)

                parse_keys(ui, keys)

                ui.flush()
                g13.write_lcd_bg()
            except usb1.USBError as e:
                if e.value == -7:
                    pass
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print('^C')
    finally:
        g13.close()


def parse_keys(ui, keys):
    if not any(keys.keys):
        ui.clear_keys()
        return

    for i, key in enumerate(G13_KEYS):
        b = keys.keys[i / 8]
        ui.set_key(key, b & 1 << (i % 8))


if __name__ == '__main__':
    lcd_only_ui()
