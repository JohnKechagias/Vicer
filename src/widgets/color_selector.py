from functools import partial
import clipboard

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .constants import *



class ColorSelector(ttk.Frame):
    def __init__(
        self,
        master=None,
        color: RGB = (75, 75, 75),
        foreground_threshold: int = 300
        ):
        """ Initializes `ColorSelector` widget.

        Args:
            master: Parent widget.
            color: Default color.
            foreground_threshold: Threshold that dictates when
                the foreground of the `colored_button` alternates
                between black and white.
        """
        super().__init__(master)

        self.colors = {'red': {}, 'green': {}, 'blue': {}}
        self.colors['red']['style'] = DANGER
        self.colors['green']['style'] = SUCCESS
        self.colors['blue']['style'] = DEFAULT

        # Theshold that dictates the color of the colored button
        # foreground. Whem the button bg is dark, the fg is white
        # and when the bg is bright, the fg is black
        self.foreground_threshold = foreground_threshold

        # Is used to lock and unlock event handlers like a mutex
        self.update_in_progress = False

        for i, (channel_name, channel) in enumerate(self.colors.items()):
            channel['value'] = tk.IntVar(value=color[i])

            channel['frame'] = ttk.Frame(master=self)
            channel['frame'].pack(fill=X, expand=YES, pady=3)

            channel['entry'] = ttk.Entry(master=channel['frame'],
                width=3,
                textvariable=channel['value']
            )
            channel['entry'].pack(side=LEFT)

            channel['scale'] = ttk.Scale(
                master=channel['frame'],
                orient=HORIZONTAL,
                bootstyle=channel['style'],
                variable=channel['value'],
                value=75,
                to=255
            )
            channel['scale'].pack(
                side=RIGHT,
                fill=X,
                expand=YES,
                padx=6,
                pady=6
            )

            channel['value'].trace_add('write',
                partial(self.update_color_value, channel_name))
            channel['entry'].bind('<Any-KeyPress>',
                partial(self._on_key_pressed, channel['value']), add='+')

        colored_button_frame = ttk.Frame(master=self, border=3, bootstyle=DARK)
        colored_button_frame.pack(fill=BOTH, expand=YES, pady=10)

        self.colored_button = tk.Button(
            master=colored_button_frame,
            autostyle=False,
            foreground='white',
            activeforeground='white',
            background=self.get_color_HEX(),
            activebackground=self.get_color_HEX(),
            text=self.get_color_HEX(),
            bd=0,
            highlightthickness=0
        )
        self.colored_button.pack(side=TOP, expand=YES, fill=X)
        self.colored_button.bind('<Button-1>',
            self._on_colored_button_clicked, add='+')

    @staticmethod
    def rgb_to_hex(rgb: RGB) -> Hex:
        """ Convert a rgb color to hex. """
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    def update_color_value(self, color_name: str, *_):
        """ Round color channel value and update buttons background. """
        # Normalize and update color value
        if self.update_in_progress == True: return
        try:
            temp_value = self.colors[color_name]['value'].get()
        except:
            return

        # aquire lock
        self.update_in_progress = True
        # Round the float value
        new_color_value = min(round(temp_value), 255)
        self.colors[color_name]['value'].set(new_color_value)
        self.update_button_bg()
        # release lock
        self.update_in_progress = False

    def update_button_bg(self):
        """ Set button background to be the same as the color
        that the user has selected. """
        # Sum of RGB channel values
        sum_of_color_values = sum(self.get_color_RGB())
        color_code = self.get_color_HEX()

        if sum_of_color_values > self.foreground_threshold:
            self.colored_button.configure(
                foreground='black',
                activeforeground='black'
            )
        else:
            self.colored_button.configure(
                foreground='white',
                activeforeground='white'
            )
        self.colored_button.configure(
            background=color_code,
            activebackground=color_code,
            text=color_code
        )

    def get_color_RGB(self) -> RGB:
        """ Return color in RGB form. """
        return (i['value'].get() for i in self.colors.values())

    def get_color_HEX(self) -> Hex:
        """ Return color in Hex form. """
        color_RGB_tuple = self.get_color_RGB()
        return self.rgb_to_hex(color_RGB_tuple)

    def set_color(self, color: RGB | Hex):
        """ Set `color`. """
        if isinstance(color, Hex):
            color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        for i, channel in enumerate(self.colors.values()):
            channel['value'].set(color[i])

    def _on_key_pressed(
        self,
        color_int_var: tk.IntVar,
        event: tk.Event
    ):
        """ Handles key presses from user.

        Args:
            color_int_var: The IntVar of the corresponding color.
            event: Event args.
        """
        min_value = 0
        max_value = 255

        if event.keysym == 'Right':
            # Check if the cursor is in the end of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == len(str(color_int_var.get())):
                value = color_int_var.get() + 1
                if value <= max_value:
                    color_int_var.set(value)
        elif event.keysym == 'Left':
            # Check if the cursor is at the start of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == 0:
                value = color_int_var.get() - 1
                if value >= min_value:
                    color_int_var.set(value)

    def _on_colored_button_clicked(self, *_):
        """ Paste the colors hex code to the clipboard. """
        clipboard.copy(self.get_color_HEX())
