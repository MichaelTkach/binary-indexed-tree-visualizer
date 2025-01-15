import tkinter as tk
from tkinter import ttk
import time

from .styles import setup_styles
from .menus import MenuManager
from ..components.bit_visualizer import BITVisualizer
from ..utils.constants import (INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT,
                               MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)


class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_styles()
        self.setup_window()
        self.create_title_bar()

        # Create menu manager and main menu
        self.menu_manager = MenuManager(self.root, self)
        self.current_frame = self.menu_manager.create_main_menu()

        self.scale_factor = 1
        self.original_geometry = None
        self.is_fullscreen = False

    def setup_styles(self):
        """Configure custom styles"""
        self.style = setup_styles()

    def setup_window(self):
        """Configure main window and controls"""
        # Set initial size and center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = round(screen_width / 2 - INITIAL_WINDOW_WIDTH / 2)
        center_y = round(screen_height / 2 - INITIAL_WINDOW_HEIGHT / 2)

        self.root.geometry(f'{INITIAL_WINDOW_WIDTH}x{INITIAL_WINDOW_HEIGHT}+{center_x}+{center_y}')
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.overrideredirect(True)  # Remove default title bar

        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_title_bar(self):
        """Create custom title bar with controls"""
        self.title_bar = ttk.Frame(self.root)
        self.title_bar.grid(row=0, column=0, sticky="ew")

        # Title
        title_label = ttk.Label(self.title_bar, text="")
        title_label.pack(side=tk.LEFT, padx=10)

        # Window controls
        controls_frame = ttk.Frame(self.title_bar)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Toggle fullscreen button
        self.toggle_button = ttk.Button(
            controls_frame,
            text="🔲",
            command=self.toggle_fullscreen,
            style='Toggle.TButton'
        )
        self.toggle_button.pack(side=tk.LEFT)

        # Close button
        close_button = ttk.Button(
            controls_frame,
            text="✕",
            command=self.on_closing,
            style='Close.TButton'
        )
        close_button.pack(side=tk.LEFT)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if hasattr(self, 'bit_visualizer') and (self.bit_visualizer.animation_running or
                                                self.bit_visualizer.step_in_progress):
            return

        if not self.is_fullscreen:
            # Going to fullscreen
            self.original_geometry = self.root.geometry()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.toggle_button.configure(text="⧉")

            # Calculate scale factors
            width_scale = screen_width / INITIAL_WINDOW_WIDTH
            height_scale = screen_height / INITIAL_WINDOW_HEIGHT
            scale_factor = (width_scale + height_scale) / 2

            # Update text sizes throughout the interface
            self._scale_interface_text(scale_factor)

            if hasattr(self, 'bit_visualizer'):
                self.scale_factor = scale_factor
                self.bit_visualizer.canvas.config(
                    width=screen_width * scale_factor,
                    height=screen_height * scale_factor
                )
                self.bit_visualizer.scale_changed("placeholder")

        else:
            # Return to normal size
            self.root.geometry(self.original_geometry)
            self._scale_interface_text(1.0)  # Reset to original scale

            if hasattr(self, 'bit_visualizer'):
                self.bit_visualizer.canvas.config(width=800, height=600)
                self.scale_factor = 1.0
                self.bit_visualizer.scale_changed("placeholder")

        self.is_fullscreen = not self.is_fullscreen

    def _scale_interface_text(self, scale_factor):
        """Scale all interface text elements"""
        style = ttk.Style()

        # Update basic text
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Text):
                widget.configure(font=('Arial', round(11 * scale_factor)))
            elif isinstance(widget, ttk.Label):
                if 'bold' in str(widget.cget('font')):
                    base_size = 24
                else:
                    base_size = 11
                widget.configure(font=('Arial', round(base_size * scale_factor)))

        # Update styles
        style.configure('Custom.TButton',
                        font=('Arial', round(12 * scale_factor)),
                        padding=(round(20 * scale_factor), round(10 * scale_factor)))
        style.configure('Menu.TButton',
                        font=('Arial', round(14 * scale_factor), 'bold'),
                        padding=(round(30 * scale_factor), round(15 * scale_factor)))
        style.configure('Control.TButton',
                        font=('Arial', round(11 * scale_factor)),
                        padding=(round(15 * scale_factor), round(8 * scale_factor)))
        style.configure('Custom.TLabelframe.Label',
                        font=('Arial', round(11 * scale_factor), 'bold'))
        style.configure('Title.TLabel',
                        font=('Arial', round(24 * scale_factor), 'bold'))

    def open_bit_builder(self):
        """Open BIT visualization window"""
        self.clear_main_frame()
        builder_frame = ttk.Frame(self.root)
        builder_frame.grid(row=1, column=0, sticky="nsew")
        self.bit_visualizer = BITVisualizer(builder_frame, self)

    def show_algorithm_description(self):
        """Show algorithm description"""
        self.menu_manager.show_algorithm_description()

    def show_interface_guide(self):
        """Show interface guide"""
        self.menu_manager.show_interface_guide()

    def return_to_menu(self, frame):
        """Return to main menu"""
        if hasattr(self, 'bit_visualizer'):
            self.bit_visualizer.is_cleaning_up = True
            self.bit_visualizer.animation_running = False
            self.bit_visualizer.paused = True
            self.bit_visualizer.step_in_progress = False
            time.sleep(0.1)
            delattr(self, 'bit_visualizer')

        frame.destroy()
        self.current_frame = self.menu_manager.create_main_menu()

    def clear_main_frame(self):
        """Clear current content from main frame"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = None

    def on_closing(self):
        """Handle window closing"""
        self.root.quit()

    def run(self):
        """Start the application"""
        self.root.mainloop()