import datetime
import threading
import cairo
from LikeAG13 import G13Device, LedColors
from LikeAG13.lcd_buffer import write_disp_matrix


class G13Lcd(G13Device):
    def __init__(self):
        super(G13Lcd, self).__init__()
        self.lock = threading.Lock()

        self.prev_x = 0
        self.prev_y = 0

        self.surface = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.LCD_WIDTH, self.LCD_HEIGHT)
        self.context = cairo.Context(self.surface)

        self.context.set_source_rgb(1, 1, 1)
        self.context.select_font_face('sans serif')
        self.context.set_font_size(10)

    def reset(self):
        self.context.set_operator(cairo.OPERATOR_CLEAR)
        self.context.paint()
        self.context.set_operator(cairo.OPERATOR_OVER)
        self.context.select_font_face('sans serif')
        self.context.set_font_size(10)

    def print_time(self):
        self.reset()

        width, height = self.context.text_extents('aA')[2:4]
        print(self.context.text_extents('aA'))
        self.context.move_to(0, height)
        text = datetime.datetime.now().strftime('%I:%M:%S')
        print(text)

        self.context.show_text(text)
        self.draw_surface()

    def draw_image(self, filename, scale=1, offset=(0, 0)):
        self.context.save()
        new_surface = cairo.ImageSurface.create_from_png(filename)
        self.context.scale(scale, scale)
        self.context.set_source_surface(new_surface, *offset)
        self.context.paint()
        self.context.restore()
        self.draw_surface()

    def draw_surface(self):
        source = self.surface.get_data()
        self.surface.write_to_png('surface_data.png')
        destination_buffer = self.get_new_buffer()
        width = self.LCD_WIDTH
        threshold = 128
        destination_buffer = write_disp_matrix(width, threshold, source, destination_buffer)
        self.update_lcd_from_buffer(destination_buffer)

    def update_lcd_from_pixels(self):
        if self.lock.acquire(False):
            super(G13Lcd, self).update_lcd_from_pixels()
            self.lock.release()

    def write_lcd_bg(self):
        threading.Thread(target=self.update_lcd_from_pixels).start()

    def print_block(self, x, y, val):
        self.set_pixel(x, y, val)
        self.set_pixel(x + 1, y, val)
        self.set_pixel(x, y + 1, val)
        self.set_pixel(x + 1, y + 1, val)

    def print_stick(self, x, y):
        x = x * 158 / 255
        y = y * 41 / 255
        self.print_block(self.prev_x, self.prev_y, 0)
        self.print_block(x, y, 1)
        self.prev_x, self.prev_y = x, y
