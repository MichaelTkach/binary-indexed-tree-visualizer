import tkinter as tk

class ResizingCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.width = kwargs.get('width', 800)
        self.height = kwargs.get('height', 600)
        self.scale_factor = 1.0
        self.allow_scaling = False

    def on_resize(self, event):
        if self.width != event.width or self.height != event.height:
            wscale = float(event.width) / self.width
            hscale = float(event.height) / self.height

            self.width = event.width
            self.height = event.height

            self.config(width=self.width, height=self.height)

            if self.allow_scaling:
                print(f"Old scale factor = {self.scale_factor}")
                self.scale_factor *= wscale
                print(f"New scale factor = {self.scale_factor}")
                self.scale("all", 0, 0, wscale, hscale)

    def set_scaling_allowed(self, allowed):
        """Enable or disable scaling"""
        self.allow_scaling = allowed