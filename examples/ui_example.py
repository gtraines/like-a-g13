from __future__ import print_function

import datetime
import sys
import threading
import time

import usb1

from LikeAG13 import G13Lcd, G13_KEYS, LedColors, MissingG13Error


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


def lcd_only_ui_colors():
    g13 = try_get_g13()

    g13.draw_image('x.png', scale=0.2, offset=(200, 0))

    g13.set_led_mode(16)

    try:
        while True:  # for i in range(300):

            # YELLOW
            g13.print_text('255 0 0')
            g13.set_color_from_rgb(255, 0, 0)
            time.sleep(1)

            # WHITE
            g13.print_text('WHITE')
            g13.set_color_from_rgb(180, 180, 180)
            time.sleep(1)

            # TEAL
            g13.print_text('0 255 0')
            g13.set_color_from_rgb(0, 255, 0)
            time.sleep(1)

            # PINK
            g13.print_text('PINK')
            g13.set_color_from_rgb(200, 200, 200)
            time.sleep(1)

            # MAGENTA
            g13.print_text('MAGENTA')
            g13.set_color_from_rgb(40, 30, 200)
            time.sleep(1)

            # # LIGHTS OUT
            # g13.print_text('0 0 0')
            # g13.set_color_from_rgb(0, 0, 0)
            # time.sleep(1)

            for value0 in range(0, 255, 5):
                for value1 in range(0, 255, 5):
                    for value2 in range(0, 255, 5):

                        g13.print_text('{} {} {}'.format(value0, value1, value2))
                        g13.set_color_from_rgb(value0, value1, value2)
                        time.sleep(0.1)
                        try:
                            keypress = g13.get_key_press_bytes()
                            if keypress is not None:
                                print(keypress)
                        except Exception as ex:
                            print(ex)


                        #
                        # parsed_version = g13.parse_keys()
                        # if parsed_version is not None:
                        #     print('parsed version: ')
                        #     print(parsed_version)

                        # g13.print_text('AQUA')
            # g13.set_color_from_named_color(LedColors.AQUA)
            # time.sleep(1)
            #
            # g13.print_text('BLUE')
            # g13.set_color_from_named_color(LedColors.BLUE)
            # time.sleep(1)
            #
            # g13.print_text('FUSCHIA')
            # g13.set_color_from_named_color(LedColors.FUSCHIA)
            # time.sleep(1)
            #
            # g13.print_text('GREEN')
            # g13.set_color_from_named_color(LedColors.GREEN)
            # time.sleep(1)
            #
            # g13.print_text('LIME')
            # g13.set_color_from_named_color(LedColors.LIME)
            # time.sleep(1)
            #
            # g13.print_text('MAROON')
            # g13.set_color_from_named_color(LedColors.MAROON)
            # time.sleep(1)
            #
            # g13.print_text('PINK')
            # g13.set_color_from_named_color(LedColors.PINK)
            # time.sleep(1)
            #
            # g13.print_text('PURPLE')
            # g13.set_color_from_named_color(LedColors.PURPLE)
            # time.sleep(1)
            #
            # g13.print_text('RED')
            # g13.set_color_from_named_color(LedColors.RED)
            # time.sleep(1)
            #
            # g13.print_text('YELLOW')
            # g13.set_color_from_named_color(LedColors.YELLOW)
            # time.sleep(1)
            #

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
                keys = g13.get_key_press_bytes()

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
    lcd_only_ui_colors()
