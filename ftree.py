import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import math
import json


class ResizingCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.width = kwargs.get('width', 800)
        self.height = kwargs.get('height', 600)
        self.scale_factor = 1.0
        self.allow_scaling = False  # Add flag to control when scaling is allowed

    def on_resize(self, event):
        # Only resize if dimensions actually changed
        if self.width != event.width or self.height != event.height:
            # Calculate scale factors
            wscale = float(event.width) / self.width
            hscale = float(event.height) / self.height

            self.width = event.width
            self.height = event.height

            # Resize the canvas
            self.config(width=self.width, height=self.height)

            # Only apply scaling if explicitly allowed (during fullscreen toggle)
            if self.allow_scaling:
                print(f"Old scale factor = {self.scale_factor}")
                self.scale_factor *= wscale
                print(f"New scale factor = {self.scale_factor}")
                self.scale("all", 0, 0, wscale, hscale)

    def set_scaling_allowed(self, allowed):
        """Enable or disable scaling"""
        self.allow_scaling = allowed

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        # self.root.title("Binary Indexed Tree Visualizer")

        # Configure custom styles
        self.setup_styles()
        self.setup_window()
        self.create_main_menu()
        self.scale_factor = 1


    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()

        # Common button style with rounded corners and modern look
        style.configure(
            'Custom.TButton',
            padding=(20, 10),
            font=('Arial', 12),
            width=13,
            borderwidth=2,
            relief="raised",
            background="#4a90e2",
            foreground="white"
        )
        style.map('Custom.TButton',
                  background=[('pressed', '#a1d4e4'), ('active', '#5db0e4'), ('disabled', '#4a90e2')],
                  relief=[('pressed', 'sunken')],
                  foreground=[('pressed', 'white'), ('active', 'cyan'), ('disabled', 'black')]
                  )

        # Main menu buttons - larger and more prominent
        style.configure(
            'Menu.TButton',
            padding=(30, 15),
            font=('Arial', 14, 'bold'),
            width=100,  # Make buttons wider
            borderwidth=2,
            relief="raised",
            background="#4a90e2",
            foreground="white"
        )
        style.map('Menu.TButton',
                  background=[('pressed', '#a1d4e4'), ('active', '#5db0e4'), ('disabled', '#4a90e2')],
                  relief=[('pressed', 'sunken')],
                  foreground=[('pressed', 'white'), ('active', 'cyan'), ('disabled', 'black')]
                  )

        # Control panel button style
        style.configure(
            'Control.TButton',
            padding=(15, 8),
            font=('Arial', 11),
            borderwidth=2,
            width=10,
            relief="raised",
            background="#31b834",
            foreground = "white"
        )
        style.map('Control.TButton',
                  background=[('pressed', '#b9e4c1'), ('active', '#6dca61'), ('disabled', '#dbd3e6')],
                  relief=[('pressed', 'sunken')],
                  foreground=[('pressed', 'white'), ('active', 'yellow'), ('disabled', 'black')]
                  )

        # Frame styles
        style.configure(
            'Custom.TLabelframe',
            borderwidth=2,
            relief="solid",
            padding=10
        )

        style.configure(
            'Custom.TLabelframe.Label',
            font=('Arial', 11, 'bold')
        )

        # Radio button style
        style.configure(
            'Custom.TRadiobutton',
            font=('Arial', 11, 'bold'),
            padding=5
        )

        # Entry style
        style.configure(
            'Custom.TEntry',
            padding=5,
            font=('Arial', 11),
        )

        # Scale style
        style.configure(
            'Custom.Horizontal.TScale',
            sliderthickness=20,
            sliderrelief="raised"
        )

        style.configure(
            'Title.TLabel',
            font=('Arial', 24, 'bold')
        )

    def setup_window(self):
        """Configure main window and controls"""
        # Set initial size and center window
        window_width = 1400
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = round(screen_width / 2 - window_width / 2)
        center_y = round(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.minsize(1400, 800)

        # Add window controls
        self.root.overrideredirect(True)  # Remove default title bar
        self.create_title_bar()

        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


    def create_title_bar(self):
        """Create custom title bar with controls"""
        self.title_bar = ttk.Frame(self.root)
        self.title_bar.grid(row=0, column=0, sticky="ew")

        # Store original window size and state
        self.original_geometry = None
        self.is_fullscreen = False

        # Title
        # title_label = ttk.Label(self.title_bar, text="Binary Indexed Tree Visualizer")
        title_label = ttk.Label(self.title_bar, text="")
        title_label.pack(side=tk.LEFT, padx=10)

        # Window controls
        controls_frame = ttk.Frame(self.title_bar)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Toggle fullscreen button
        self.toggle_button = ttk.Button(controls_frame, text="🔲",
                                        command=self.toggle_fullscreen,
                                        style='Toggle.TButton')
        self.toggle_button.pack(side=tk.LEFT)

        # Close button
        close_button = ttk.Button(controls_frame, text="✕",
                                  command=self.on_closing,
                                  style='Close.TButton')
        close_button.pack(side=tk.LEFT)

    def create_main_menu(self):
        """Create enhanced main menu with modern styling"""
        menu_frame = ttk.Frame(self.root)
        menu_frame.grid(row=1, column=0, sticky="nsew")
        menu_frame.grid_rowconfigure(0, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)

        # Create centered content frame
        content_frame = ttk.Frame(menu_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title with scaled font
        title = ttk.Label(
            content_frame,
            text="Binary Indexed Tree Visualizer",
            style='Title.TLabel'
        )
        title.pack(pady=(0, 40))

        # Calculate button dimensions based on screen size
        button_width = 30  # Base width
        button_pady = 20  # Base padding

        # Create button container that will scale with window
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Create adaptable buttons
        build_button = ttk.Button(
            buttons_frame,
            text="Build BIT",
            command=self.open_bit_builder,
            style='Menu.TButton',
            width=button_width
        )
        build_button.pack(pady=button_pady, fill=tk.X)

        desc_button = ttk.Button(
            buttons_frame,
            text="Algorithm Description",
            command=self.show_algorithm_description,
            style='Menu.TButton',
            width=button_width
        )
        desc_button.pack(pady=button_pady, fill=tk.X)

        guide_button = ttk.Button(
            buttons_frame,
            text="Interface Guide",
            command=self.show_interface_guide,
            style='Menu.TButton',
            width=button_width
        )
        guide_button.pack(pady=button_pady, fill=tk.X)


    def open_bit_builder(self):
        """Open BIT visualization window"""
        self.clear_main_frame()
        builder_frame = ttk.Frame(self.root)
        builder_frame.grid(row=1, column=0, sticky="nsew")

        # Create BIT visualizer
        self.bit_visualizer = BITVisualizer(builder_frame, self)

    def update_text_scaling(self, event, text_widget, title_widget):
        """Update text scaling when window size changes"""
        if event.widget == self.root:
            try:
                # Recalculate scale factor
                width_scale = event.width / 1400
                height_scale = event.height / 800
                scale_factor = min(width_scale, height_scale)

                # Update font sizes
                title_size = round(28 * scale_factor)
                heading_size = round(16 * scale_factor)
                text_size = round(11 * scale_factor)

                # Update text widget fonts if widgets still exist
                text_widget.tag_configure('heading', font=('Arial', heading_size, 'bold'))
                text_widget.tag_configure('normal', font=('Arial', text_size))
                text_widget.tag_configure('bullet', font=('Arial', text_size))
                title_widget.configure(font=('Arial', title_size, 'bold'))
            except tk.TclError:
                # If widgets are destroyed, remove the binding
                if self.current_configure_binding:
                    self.root.unbind('<Configure>', self.current_configure_binding)
                    self.current_configure_binding = None

    def show_algorithm_description(self):
        """Show enhanced algorithm description window with proper text scaling"""
        self.clear_main_frame()
        desc_frame = ttk.Frame(self.root)
        desc_frame.grid(row=1, column=0, sticky="nsew")

        # Create content frame
        content_frame = ttk.Frame(desc_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Calculate base font sizes and scale factor
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        width_scale = window_width / 1400
        height_scale = window_height / 800
        scale_factor = min(width_scale, height_scale)

        title_size = round(28 * scale_factor)
        heading_size = round(16 * scale_factor)
        text_size = round(11 * scale_factor)

        # Add "Back to Menu" button with scaled font
        back_button = ttk.Button(
            content_frame,
            text="← Back to Menu",
            command=lambda: self.return_to_menu(desc_frame),
            style='Custom.TButton'
        )
        back_button.pack(pady=(5, 15), anchor='w')

        # Add title with scaled font
        title = ttk.Label(
            content_frame,
            text="Binary Indexed Tree (BIT)",
            font=('Arial', title_size, 'bold')
        )
        title.pack(pady=(0, 20))

        # Create text container frame
        text_container = ttk.Frame(content_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        # Create text widget with scaled font
        text = tk.Text(
            text_container,
            wrap=tk.WORD,
            padx=20,
            pady=20,
            font=('Arial', text_size),
            bg='#f5f5f5'
        )
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.configure(yscrollcommand=scrollbar.set)

        # Configure text tags
        text.tag_configure('heading', font=('Arial', heading_size, 'bold'))
        text.tag_configure('normal', font=('Arial', text_size))
        text.tag_configure('bullet', font=('Arial', text_size))

        # Content for the algorithm description
        description = """# Overview
A Binary Indexed Tree (BIT), also known as a Fenwick Tree, is an efficient data structure 
for calculating and manipulating prefix sums in an array.

# Key Features
• Space Efficient: Uses O(n) space
• Time Efficient: O(log n) for both query and update operations
• Easy Implementation: Simpler than segment trees

# Operations
1. Update Operation
   - Modify a value in the array
   - Time Complexity: O(log n)

2. Query Operation
   - Get sum of elements from index 1 to i
   - Time Complexity: O(log n)

# Implementation Details
The structure uses a binary representation of indices to store partial sums
in a way that enables efficient updates and queries. Each node in the tree
represents a range of elements from the original array.

# Advantages
1. Fast Updates: Maintains dynamic prefix sums with quick updates
2. Memory Efficient: Requires exactly the same space as the input array
3. Simple Implementation: Easier to code than other similar data structures

[Space for Additional Content and Screenshots...]"""

        # Insert text with proper formatting
        lines = description.split('\n')
        for line in lines:
            if line.startswith('# '):
                text.insert(tk.END, line[2:] + '\n', 'heading')
            elif line.startswith('• '):
                text.insert(tk.END, line + '\n', 'bullet')
            else:
                text.insert(tk.END, line + '\n', 'normal')

        text.configure(state='disabled')

        # Set up configure binding
        self.current_configure_binding = self.root.bind(
            '<Configure>',
            lambda e: self.update_text_scaling(e, text, title)
        )

    def show_interface_guide(self):
        """Show enhanced interface guide window with proper text scaling"""
        self.clear_main_frame()
        guide_frame = ttk.Frame(self.root)
        guide_frame.grid(row=1, column=0, sticky="nsew")

        # Create content frame
        content_frame = ttk.Frame(guide_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Calculate base font sizes and scale factor
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        width_scale = window_width / 1400
        height_scale = window_height / 800
        scale_factor = min(width_scale, height_scale)

        title_size = round(28 * scale_factor)
        heading_size = round(16 * scale_factor)
        text_size = round(11 * scale_factor)

        # Add "Back to Menu" button with scaled font
        back_button = ttk.Button(
            content_frame,
            text="← Back to Menu",
            command=lambda: self.return_to_menu(guide_frame),
            style='Custom.TButton'
        )
        back_button.pack(pady=(5, 15), anchor='w')

        # Add title with scaled font
        title = ttk.Label(
            content_frame,
            text="Interface Guide",
            font=('Arial', title_size, 'bold')
        )
        title.pack(pady=(0, 20))

        # Create text container frame
        text_container = ttk.Frame(content_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        # Create text widget with scaled font
        text = tk.Text(
            text_container,
            wrap=tk.WORD,
            padx=20,
            pady=20,
            font=('Arial', text_size),
            bg='#f5f5f5'
        )
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.configure(yscrollcommand=scrollbar.set)

        # Configure text tags
        text.tag_configure('heading', font=('Arial', heading_size, 'bold'))
        text.tag_configure('normal', font=('Arial', text_size))
        text.tag_configure('bullet', font=('Arial', text_size))

        # Content for the interface guide
        guide = """# Building BIT
• Enter comma-separated numbers in the input field
• Click Initialize to create the structure
• Use animation controls to visualize the building process

# Animation Controls
• Automatic Mode
  - Start: Begin automatic animation
  - Stop: Pause the animation
  - Speed: Adjust animation speed

• Manual Mode
  - Previous: Go back one step
  - Next: Advance one step
  - Scale: Change visualization size

# File Operations
• Load: Open a saved BIT configuration
• Save: Store current visualization state

# Window Controls
• Toggle fullscreen mode (🔲 button)
• Close application (✕ button)

[Space for additional screenshots and examples...]"""

        # Insert text with proper formatting
        lines = guide.split('\n')
        for line in lines:
            if line.startswith('# '):
                text.insert(tk.END, line[2:] + '\n', 'heading')
            elif line.startswith('• '):
                text.insert(tk.END, line + '\n', 'bullet')
            else:
                text.insert(tk.END, line + '\n', 'normal')

        text.configure(state='disabled')

        # Set up configure binding
        self.current_configure_binding = self.root.bind(
            '<Configure>',
            lambda e: self.update_text_scaling(e, text, title)
        )

    def return_to_menu(self, frame):
        """Return to main menu with proper cleanup"""
        # Clean up any existing configure binding
        if hasattr(self, 'current_configure_binding') and self.current_configure_binding:
            self.root.unbind('<Configure>', self.current_configure_binding)
            self.current_configure_binding = None

        if hasattr(self, 'bit_visualizer'):
            # Stop any running animation and mark for cleanup
            self.bit_visualizer.is_cleaning_up = True
            self.bit_visualizer.animation_running = False
            self.bit_visualizer.paused = True
            self.bit_visualizer.step_in_progress = False

            # Wait a brief moment for any ongoing operations to stop
            time.sleep(0.1)

            # Clean up the bit_visualizer
            delattr(self, 'bit_visualizer')

        frame.destroy()
        self.create_main_menu()

    def clear_main_frame(self):
        """Clear current content from main frame"""
        for widget in self.root.grid_slaves(row=1):
            widget.destroy()


    def toggle_fullscreen(self):
        if hasattr(self, 'bit_visualizer') and (self.bit_visualizer.animation_running or
                                                self.bit_visualizer.step_in_progress):
            return

        if not self.is_fullscreen:
            # Going to fullscreen
            self.original_geometry = self.root.geometry()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            print(f"Screen width {screen_width} screen height {screen_height}")
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.toggle_button.configure(text="⧉")

            # Calculate scale factors for the current screen
            width_scale = screen_width / 1400  # Base window width
            height_scale = screen_height / 800  # Base window height
            scale_factor = (width_scale + height_scale) / 2

            # Update text sizes throughout the interface
            self._scale_interface_text(scale_factor)

            if hasattr(self, 'bit_visualizer'):

                self.scale_factor = scale_factor
                self.bit_visualizer.canvas.config(width=(screen_width - 0) * scale_factor,
                                                  height=(screen_height - 0) * scale_factor)

                self.bit_visualizer.scale_changed("placeholder")
        else:
            # Return to normal size
            self.root.geometry(self.original_geometry)

            # Reset text sizes to original
            self._scale_interface_text(1.0)  # Reset to original scale

            if hasattr(self, 'bit_visualizer'):
                self.bit_visualizer.canvas.config(width=800, height=600)

                self.scale_factor = 1.0
                self.bit_visualizer.scale_changed("placeholder")

        self.is_fullscreen = not self.is_fullscreen

    def _scale_interface_text(self, scale_factor):
        """Scale all interface text elements"""
        # Find all Text widgets in the application
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Text):
                # Scale text widget fonts
                base_size = 11  # Base font size for regular text
                new_size = round(base_size * scale_factor)
                widget.configure(font=('Arial', new_size))

                # Scale text tags if they exist
                try:
                    widget.tag_configure('heading', font=('Arial', round(16 * scale_factor), 'bold'))
                    widget.tag_configure('normal', font=('Arial', round(11 * scale_factor)))
                    widget.tag_configure('bullet', font=('Arial', round(11 * scale_factor)))
                except tk.TclError:
                    pass  # Tag doesn't exist

            elif isinstance(widget, ttk.Label):
                # Scale label fonts
                if 'bold' in str(widget.cget('font')):
                    # This is a title or heading
                    base_size = 24  # Base size for titles
                else:
                    base_size = 11  # Base size for regular labels
                new_size = round(base_size * scale_factor)
                widget.configure(font=('Arial', new_size, 'bold' if 'bold' in str(widget.cget('font')) else ''))

        # Update ttk styles for buttons
        style = ttk.Style()
        style.configure('Custom.TButton', font=('Arial', round(12 * scale_factor)),
                        borderwidth=round(2 * scale_factor),
                        padding=(round(20 * scale_factor), round(10 * scale_factor)),
                        width=round(13 * scale_factor))
        style.configure('Menu.TButton', font=('Arial', round(14 * scale_factor), 'bold'),
                        borderwidth=round(2 * scale_factor),
                        padding=(round(30 * scale_factor), round(15 * scale_factor)),
                        width=round(30 * scale_factor))
        style.configure('Custom.TLabelframe', borderwidth=round(2 * scale_factor),
                        padding=round(10 * scale_factor))
        style.configure('Title.TLabel', font=('Arial', round(24 * scale_factor), 'bold'))
        style.configure('Control.TButton', font=('Arial', round(11 * scale_factor)),
                        borderwidth=round(2 * scale_factor),
                        padding=(round(15 * scale_factor), round(8 * scale_factor)),
                        width=round(10 * scale_factor))
        style.configure('Custom.TEntry', font=('Arial', round(11 * scale_factor)),
                        padding=round(5 * scale_factor))
        style.configure('Custom.Horizontal.TScale', sliderthickness=round(20 * scale_factor))
        style.configure('Custom.TLabelframe.Label', font=('Arial', round(11 * scale_factor), 'bold'))
        style.configure('Custom.TRadiobutton', font=('Arial', round(11 * scale_factor), 'bold'),
                        padding=round(5 * scale_factor))

    def on_closing(self):
        """Handle window closing"""
        self.root.quit()

    def run(self):
        """Start the application"""
        self.root.mainloop()

class BITVisualizer:
    def __init__(self, parent, application):
        self.parent = parent
        self.is_cleaning_up = False
        self.application = application

        # Control panel with adaptive sizing
        self.control_panel = ttk.Frame(parent)
        self.control_panel.pack(fill=tk.X, padx=5, pady=5)

        # Create styled control panel
        self.create_styled_control_panel()

        # Canvas setup with scrollbars and adaptability
        self.canvas_frame = ttk.Frame(parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Replace the canvas creation with ResizingCanvas
        self.canvas = ResizingCanvas(self.canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Add a tag to all drawn items for scaling
        def tag_all_after_draw(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self.canvas.addtag_all("all")
                return result

            return wrapper

        # Decorate drawing methods
        self.draw_initial_state = tag_all_after_draw(self.draw_initial_state)
        self.execute_step = tag_all_after_draw(self.execute_step)

        # Always visible scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical",
                                         command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal",
                                         command=self.canvas.xview)

        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set,
                              xscrollcommand=self.h_scrollbar.set)

        # Bind to resize events
        self.parent.bind('<Configure>', self.on_resize)

        # State variables
        self.animation_running = False
        self.initialized = False
        self.current_step = 0
        self.step_in_progress = False
        self.paused = False
        self.animation_thread = None
        self.animation_steps = []
        self.nodes = {}
        self.arrows = {}
        self.bit_array = []
        self.initial_array = []

        # Initialize controls
        self.update_controls()

    def create_styled_control_panel(self):
        """Create enhanced control panel with modern styling"""
        # Calculate paddings and sizes based on scale factor
        scale_factor = self.application.scale_factor
        base_padding = round(5 * scale_factor)
        frame_padding = round(10 * scale_factor)

        # Back to Menu button at the very top
        back_frame = ttk.Frame(self.control_panel)
        back_frame.pack(fill=tk.X, pady=(0, base_padding))

        self.back_button = ttk.Button(
            back_frame,
            text="← Back to Menu",
            command=lambda: self.application.return_to_menu(self.parent),
            style='Custom.TButton'
        )
        self.back_button.pack(anchor='w', padx=20, pady=20)

        # File operations frame
        self.file_frame = ttk.LabelFrame(
            self.control_panel,
            text="File Operations",
            style='Custom.TLabelframe',
            padding=frame_padding
        )
        self.file_frame.pack(side=tk.LEFT, padx=base_padding, fill=tk.BOTH)

        file_buttons = ttk.Frame(self.file_frame)
        file_buttons.pack(fill=tk.X, expand=True)

        # Create buttons that will expand proportionally
        self.load_button = ttk.Button(
            file_buttons,
            text="Load",
            command=self.load_from_file,
            style='Control.TButton'
        )
        self.load_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

        self.save_button = ttk.Button(
            file_buttons,
            text="Save",
            command=self.save_to_file,
            style='Control.TButton'
        )
        self.save_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

        # Input section
        self.input_frame = ttk.LabelFrame(
            self.control_panel,
            text="Input",
            style='Custom.TLabelframe',
        )
        self.input_frame.pack(side=tk.LEFT, padx=base_padding, fill=tk.BOTH, expand=True)

        input_content = ttk.Frame(self.input_frame)
        input_content.pack(fill=tk.X, expand=True)

        self.input_label = ttk.Label(input_content, text="Array:", style='Custom.TLabelframe.Label')
        self.input_label.pack(side=tk.LEFT, padx=base_padding)

        self.input_entry = ttk.Entry(input_content, style='Custom.TEntry')
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

        self.init_button = ttk.Button(
            input_content,
            text="Initialize",
            command=self.initialize_bit,
            style='Control.TButton'
        )
        self.init_button.pack(side=tk.LEFT, padx=base_padding)

        # Animation Controls
        self.anim_frame = ttk.LabelFrame(
            self.control_panel,
            text="Animation Controls",
            style='Custom.TLabelframe',
            padding=frame_padding
        )
        self.anim_frame.pack(side=tk.LEFT, padx=base_padding, fill=tk.BOTH)

        # Mode selection with equal spacing
        mode_frame = ttk.Frame(self.anim_frame)
        mode_frame.pack(fill=tk.X, expand=True)

        self.mode_var = tk.StringVar(value="automatic")
        self.auto_radio = ttk.Radiobutton(
            mode_frame,
            text="Automatic",
            variable=self.mode_var,
            value="automatic",
            command=self.mode_changed,
            style='Custom.TRadiobutton'
        )
        self.manual_radio = ttk.Radiobutton(
            mode_frame,
            text="Manual",
            variable=self.mode_var,
            value="manual",
            command=self.mode_changed,
            style='Custom.TRadiobutton'
        )

        # Center radio buttons
        self.auto_radio.pack(side=tk.LEFT, expand=True)
        self.manual_radio.pack(side=tk.LEFT, expand=True)

        # Control buttons that expand proportionally
        self.button_frame = ttk.Frame(self.anim_frame)
        self.button_frame.pack(fill=tk.X, pady=base_padding)

        # Control buttons with equal width and expanding to fill space
        self.start_button = ttk.Button(self.button_frame, text="Start",
                                       command=self.start_animation,
                                       style='Control.TButton')
        self.stop_button = ttk.Button(self.button_frame, text="Stop",
                                      command=self.stop_animation,
                                      style='Control.TButton')
        self.prev_button = ttk.Button(self.button_frame, text="Previous",
                                      command=self.prev_step,
                                      style='Control.TButton')
        self.next_button = ttk.Button(self.button_frame, text="Next",
                                      command=self.next_step,
                                      style='Control.TButton')

        # Sliders frame
        slider_frame = ttk.Frame(self.anim_frame)
        slider_frame.pack(fill=tk.X, pady=base_padding)

        # Scale and Speed controls that expand proportionally
        for control, label in [('scale', 'Scale:'), ('speed', 'Speed:')]:
            frame = ttk.Frame(slider_frame)
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

            ttk.Label(frame, text=label, style='Custom.TLabelframe.Label').pack(side=tk.LEFT)

            if control == 'scale':
                self.scale_value = tk.DoubleVar(value=1.0)
                self.scale_slider = ttk.Scale(
                    frame,
                    from_=0.5, to=2.0,
                    orient=tk.HORIZONTAL,
                    variable=self.scale_value,
                    command=self.scale_changed,
                    style='Custom.Horizontal.TScale'
                )
                self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)
            else:
                self.speed_scale = ttk.Scale(
                    frame,
                    from_=1, to=10.0,
                    orient=tk.HORIZONTAL,
                    style='Custom.Horizontal.TScale'
                )
                self.speed_scale.set(3.0)
                self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)


    def on_resize(self, event):
        """Handle window resize with UI adaptability"""
        if event.widget == self.parent:
            # Update scroll region
            width = self.parent.winfo_width()
            height = self.parent.winfo_height()

            # Calculate the bounding box of all items on the canvas
            bbox_tuple = self.canvas.bbox("all")
            if bbox_tuple is None:
                bbox = []
            else:
                bbox = list(bbox_tuple)

            if bbox:
                # Ensure scroll region covers at least the window size
                bbox[2] = max(bbox[2], width)
                bbox[3] = max(bbox[3], height)

                # Add padding to the scroll region
                if hasattr(self.application, 'is_fullscreen') and self.application.is_fullscreen:
                    # Use smaller padding in fullscreen mode to maintain margins
                    padding_ratio = 0.1
                else:
                    padding_ratio = 0.1 # 10% padding in normal mode

                bbox[2] = bbox[2] * (1 + padding_ratio)
                bbox[3] = bbox[3] * (1 + padding_ratio)

                self.canvas.configure(scrollregion=bbox)

    def on_closing(self):
        """Handle window closing"""
        self.root.quit()

    def initialize_bit(self, current_step=0):
        """Initialize BIT with proper scaling"""
        if self.animation_running or self.step_in_progress:
            return

        try:
            self.initial_array = list(map(int, self.input_entry.get().split(',')))
            self.bit_array = [0] * (len(self.initial_array) + 1)

            # Calculate BIT values
            for i in range(len(self.initial_array)):
                self.bit_array[i + 1] = self.initial_array[i]

            for i in range(1, len(self.bit_array)):
                parent = i + (i & -i)
                if parent < len(self.bit_array):
                    self.bit_array[parent] += self.bit_array[i]

            self.current_step = current_step
            self.scale_changed("placeholder")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid comma-separated numbers")

    def prepare_animation_steps(self, is_loaded_from_file=False):
        """Prepare sequence of animation steps with grouped animations"""
        self.animation_steps = []
        n = len(self.initial_array)

        # Calculate node positions and levels
        levels = self.calculate_levels(n)
        positions = self.calculate_positions(n, levels, is_loaded_from_file)

        # Group nodes with their immediate connections
        for i in range(1, n + 1):
            children = []
            children_values = []

            # Find all existing children for this node
            for j in range(1, i):
                if j + (j & -j) == i:
                    children.append({
                        'index': j,
                        'position': positions[j],  # Changed from 'child_pos' to 'position'
                        'value': self.bit_array[j]
                    })
                    children_values.append({
                        'from': j,
                        'value': self.bit_array[j]
                    })

            if children:  # If node has children
                self.animation_steps.append({
                    'type': 'parent_with_children',
                    'parent': {
                        'index': i,
                        'value': self.initial_array[i - 1],
                        'position': positions[i]
                    },
                    'children': children,
                    'value_transfers': children_values,
                    'final_value': self.bit_array[i]
                })
            else:  # Leaf node
                self.animation_steps.append({
                    'type': 'leaf_node',
                    'node': {
                        'index': i,
                        'value': self.initial_array[i - 1],
                        'position': positions[i]
                    }
                })

        # Add root node with all connections as single step
        root_pos = self.calculate_root_position(positions, is_loaded_from_file)
        parentless = self.find_parentless_nodes(n)
        if parentless:
            self.animation_steps.append({
                'type': 'root_with_connections',
                'position': root_pos,
                'connections': [{
                    'node': node,
                    'position': positions[node]
                } for node in parentless]
            })

    def get_array_y_position(self):
        """Calculate y position for array labels and elements"""
        scale_value = self.scale_value.get()
        self_factor = self.application.scale_factor
        scale = scale_value * self_factor

        levels = self.calculate_levels(len(self.initial_array))
        max_level = max(levels.keys())
        top_margin = 80 * scale

        # Position arrays below the diagram
        # Calculate based on the lowest node position plus some margin
        return top_margin + (max_level + 1) * 50 * scale


    def draw_initial_state(self):
        """Draw static elements with aligned spacing and proper line widths"""
        self.canvas.delete('all')

        print(f"Scale {self.scale_value.get()} | Scale factor {self.application.scale_factor}")

        scale_value = self.scale_value.get()
        scale_factor = self.application.scale_factor
        scale = scale_value * scale_factor

        # Calculate scaled line widths
        rect_line_width = self.calculate_rectangle_properties()

        left_margin = 100 * scale
        x_spacing = 50 * scale  # Use same spacing for all elements
        margin = 30 * scale

        # Draw RSB labels
        levels = self.calculate_levels(len(self.initial_array))
        y_offset = margin

        # Draw "RSB" header
        self.canvas.create_text(margin, y_offset,
                                text="RSB",
                                font=("Arial", round(12 * scale), "bold"),
                                anchor="w")

        # Draw RSB values for each level
        max_level = max(levels.keys())
        for level in sorted(levels.keys(), reverse=True):
            y = margin + (max_level - level) * 50 * scale
            nodes_at_level = levels[level]
            rsb_value = nodes_at_level[0] & -nodes_at_level[0]
            self.canvas.create_text(margin, y + 50 * scale,
                                    text=str(rsb_value),
                                    font=("Arial", round(12 * scale), "bold"),
                                    anchor="w")

        # Draw arrays with aligned spacing
        array_y = self.get_array_y_position()

        # Draw index line
        self.canvas.create_text(left_margin - 70 * scale, array_y,
                                text="Index",
                                font=("Arial", round(12 * scale), "bold"),
                                anchor="w")

        for i in range(len(self.initial_array)):
            x = left_margin + (i + 1) * x_spacing
            # Draw index
            self.canvas.create_text(x, array_y,
                                    text=str(i + 1),
                                    font=("Arial", round(12 * scale)))

            # Draw arrays
            bit_y = array_y + 30 * scale
            initial_y = bit_y + 30 * scale

            # Draw array labels
            if i == 0:
                self.canvas.create_text(left_margin - 70 * scale, bit_y,
                                        text="BIT array",
                                        font=("Arial", round(12 * scale), "bold"),
                                        anchor="w")
                self.canvas.create_text(left_margin - 70 * scale, initial_y,
                                        text="Initial array",
                                        font=("Arial", round(12 * scale), "bold"),
                                        anchor="w")

            # Draw array elements with specified rectangle line width
            box_size = 15 * scale
            # BIT array element
            self.canvas.create_rectangle(x - box_size, bit_y - box_size,
                                         x + box_size, bit_y + box_size,
                                         outline="black",
                                         width=rect_line_width)
            self.canvas.create_text(x, bit_y,
                                    text=str(self.bit_array[i + 1]),
                                    font=("Arial", round(12 * scale)))

            # Initial array element
            self.canvas.create_rectangle(x - box_size, initial_y - box_size,
                                         x + box_size, initial_y + box_size,
                                         outline="black",
                                         width=rect_line_width)
            self.canvas.create_text(x, initial_y,
                                    text=str(self.initial_array[i]),
                                    font=("Arial", round(12 * scale)))

    def draw_array_element(self, x, y, value, scale):
        """Draw array element with proper scaling for both size and line width"""
        box_size = 15 * scale
        rect_line_width = self.calculate_rectangle_properties()
        self.canvas.create_rectangle(
            x - box_size, y - box_size,
            x + box_size, y + box_size,
            outline="black",
            width=rect_line_width
        )
        self.canvas.create_text(x, y, text=str(value),
                                font=("Arial", round(12 * scale)))

    def calculate_arrow_intersection(self, x1, y1, x2, y2, r, is_loaded_from_file=False):
        """Calculate intersection point of arrow with node circle"""
        scale_value = self.scale_value.get()
        self_factor = self.application.scale_factor
        scale = scale_value * self_factor if not is_loaded_from_file else 1

        x1, x2, y1, y2, r = x1 * scale, x2 * scale, y1 * scale, y2 * scale, r * scale

        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return x2, y2

        # Scale to radius
        dx = dx / dist * r
        dy = dy / dist * r

        # Calculate intersection point
        # Arrow should touch the surface of the circle
        ix = x2 - dx
        iy = y2 - dy

        return ix, iy


    def execute_step(self, step, reverse=False, force_draw=False):
        """Execute animation step with proper reverse animations"""
        scale_value = self.scale_value.get()
        scale_factor = self.application.scale_factor
        scale = scale_value * scale_factor

        arrow_line_width, arrow_shape = self.calculate_arrow_properties()  # Scale arrow shape and width

        duration = 0 if force_draw else 1.0 / self.speed_scale.get()

        # Pass force_draw to all animation methods
        if step['type'] == 'leaf_node':
            if not reverse:
                node = step['node']
                node_ids = self.animate_node(node['position'][0], node['position'][1],
                                             node['value'], node['index'], duration, scale, force_draw)
                self.nodes[node['index']] = node_ids
            else:
                if step['node']['index'] in self.nodes:
                    node_ids = self.nodes[step['node']['index']]
                    self.animate_node_removal(node_ids, duration)
                    for item in node_ids:
                        self.canvas.delete(item)
                    del self.nodes[step['node']['index']]

        elif step['type'] == 'parent_with_children':
            if not reverse:
                # Create parent node
                parent = step['parent']
                parent_pos = parent['position']
                node_ids = self.animate_node(parent_pos[0], parent_pos[1],
                                             parent['value'], parent['index'], duration, scale)
                self.nodes[parent['index']] = node_ids

                # Draw all arrows simultaneously
                arrows_to_draw = []
                for child in step['children']:
                    start_pos = parent_pos
                    child_pos = child['position']  # Changed from 'child_pos' to 'position'

                    # Calculate intersection points
                    r = 15
                    end_x, end_y = self.calculate_arrow_intersection(
                        start_pos[0], start_pos[1], child_pos[0], child_pos[1], r)
                    start_x, start_y = self.calculate_arrow_intersection(
                        child_pos[0], child_pos[1], start_pos[0], start_pos[1], r)

                    arrow_id = self.canvas.create_line(
                        start_x, start_y, start_x, start_y,
                        arrow=tk.LAST,
                        width=arrow_line_width,
                        arrowshape=arrow_shape,
                    )
                    arrows_to_draw.append({
                        'id': arrow_id,
                        'start': (start_x, start_y),
                        'end': (end_x, end_y),
                        'child_index': child['index']
                    })
                    self.arrows[f"{parent['index']}-{child['index']}"] = arrow_id

                # Animate all arrows simultaneously
                steps = 20
                for i in range(steps):
                    if not self.animation_running and self.mode_var.get() == "automatic":
                        break
                    progress = (i + 1) / steps
                    for arrow in arrows_to_draw:
                        current_x = arrow['start'][0] + (arrow['end'][0] - arrow['start'][0]) * progress
                        current_y = arrow['start'][1] + (arrow['end'][1] - arrow['start'][1]) * progress
                        self.canvas.coords(arrow['id'],
                                           arrow['start'][0], arrow['start'][1],
                                           current_x, current_y)
                    self.canvas.update()
                    time.sleep(duration / steps)

                # Animate all value transfers simultaneously
                if 'value_transfers' in step:
                    moving_texts = []
                    for transfer in step['value_transfers']:
                        from_node = self.nodes[transfer['from']][0]
                        to_node = self.nodes[parent['index']][0]

                        from_coords = self.canvas.coords(from_node)
                        to_coords = self.canvas.coords(to_node)

                        start_x = (from_coords[0] + from_coords[2]) / 2
                        start_y = (from_coords[1] + from_coords[3]) / 2
                        end_x = (to_coords[0] + to_coords[2]) / 2
                        end_y = (to_coords[1] + to_coords[3]) / 2

                        text_id = self.canvas.create_text(
                            start_x, start_y,
                            text=str(transfer['value']),
                            fill="red",
                            font=("Arial", round(12 * scale), ))
                        moving_texts.append({
                            'id': text_id,
                            'start': (start_x, start_y),
                            'end': (end_x, end_y)
                        })

                    for i in range(steps):
                        if not self.animation_running and self.mode_var.get() == "automatic":
                            break
                        progress = (i + 1) / steps
                        for text in moving_texts:
                            current_x = text['start'][0] + (text['end'][0] - text['start'][0]) * progress
                            current_y = text['start'][1] + (text['end'][1] - text['start'][1]) * progress
                            self.canvas.coords(text['id'], current_x, current_y)
                        self.canvas.update()
                        time.sleep(duration / steps)

                    for text in moving_texts:
                        self.canvas.delete(text['id'])

                    # Update parent node value
                    self.canvas.itemconfig(self.nodes[parent['index']][1],
                                           text=str(step['final_value']))

            else:  # Reverse animation
                parent_idx = step['parent']['index']

                # First animate value transfers back to children
                if 'value_transfers' in step:
                    moving_texts = []
                    for transfer in step['value_transfers']:
                        from_node = self.nodes[parent_idx][0]
                        to_node = self.nodes[transfer['from']][0]

                        from_coords = self.canvas.coords(from_node)
                        to_coords = self.canvas.coords(to_node)

                        start_x = (from_coords[0] + from_coords[2]) / 2
                        start_y = (from_coords[1] + from_coords[3]) / 2
                        end_x = (to_coords[0] + to_coords[2]) / 2
                        end_y = (to_coords[1] + to_coords[3]) / 2

                        text_id = self.canvas.create_text(
                            start_x, start_y,
                            text=str(transfer['value']),
                            fill="red",
                            font=("Arial", round(12 * scale), ))
                        moving_texts.append({
                            'id': text_id,
                            'start': (start_x, start_y),
                            'end': (end_x, end_y)
                        })

                    steps = 20
                    for i in range(steps):
                        if not self.animation_running and self.mode_var.get() == "automatic":
                            break
                        progress = (i + 1) / steps
                        for text in moving_texts:
                            current_x = text['start'][0] + (text['end'][0] - text['start'][0]) * progress
                            current_y = text['start'][1] + (text['end'][1] - text['start'][1]) * progress
                            self.canvas.coords(text['id'], current_x, current_y)
                        self.canvas.update()
                        time.sleep(duration / steps)

                    for text in moving_texts:
                        self.canvas.delete(text['id'])

                # Then animate arrow removals
                arrows_to_remove = []
                for child in step['children']:
                    arrow_key = f"{parent_idx}-{child['index']}"  # Changed from child['child'] to child['index']
                    if arrow_key in self.arrows:
                        arrow_id = self.arrows[arrow_key]
                        coords = self.canvas.coords(arrow_id)
                        arrows_to_remove.append({
                            'id': arrow_id,
                            'start': (coords[0], coords[1]),
                            'end': (coords[2], coords[3])
                        })

                steps = 20
                for i in range(steps - 1, -1, -1):
                    progress = i / steps
                    for arrow in arrows_to_remove:
                        current_x = arrow['start'][0] + (arrow['end'][0] - arrow['start'][0]) * progress
                        current_y = arrow['start'][1] + (arrow['end'][1] - arrow['start'][1]) * progress
                        self.canvas.coords(arrow['id'],
                                           arrow['start'][0], arrow['start'][1],
                                           current_x, current_y)
                    self.canvas.update()
                    time.sleep(duration / steps)

                # Delete arrows
                for child in step['children']:
                    arrow_key = f"{parent_idx}-{child['index']}"  # Changed from child['child'] to child['index']
                    if arrow_key in self.arrows:
                        self.canvas.delete(self.arrows[arrow_key])
                        del self.arrows[arrow_key]

                # Finally remove the parent node
                if parent_idx in self.nodes:
                    self.animate_node_removal(self.nodes[parent_idx], duration)
                    for item in self.nodes[parent_idx]:
                        self.canvas.delete(item)
                    del self.nodes[parent_idx]

                # Finally remove the parent node
                if parent_idx in self.nodes:
                    self.animate_node_removal(self.nodes[parent_idx], duration)
                    for item in self.nodes[parent_idx]:
                        self.canvas.delete(item)
                    del self.nodes[parent_idx]

        elif step['type'] == 'root_with_connections':
            if not reverse:
                # Add root node
                x, y = step['position']
                self.root_node = self.animate_node(x, y, 'R', 'R', duration, scale)

                # Add all connections simultaneously
                arrows_to_draw = []
                for conn in step['connections']:
                    r = 15
                    end_x, end_y = self.calculate_arrow_intersection(
                        x, y, conn['position'][0], conn['position'][1], r)
                    start_x, start_y = self.calculate_arrow_intersection(
                        conn['position'][0], conn['position'][1], x, y, r)

                    arrow_id = self.canvas.create_line(
                        start_x, start_y, start_x, start_y,
                        arrow=tk.LAST,
                        width=arrow_line_width,
                        arrowshape=arrow_shape,
                    )
                    arrows_to_draw.append({
                        'id': arrow_id,
                        'start': (start_x, start_y),
                        'end': (end_x, end_y),
                        'node': conn['node']
                    })
                    self.arrows[f"root-{conn['node']}"] = arrow_id

                steps = 20
                for i in range(steps):
                    if not self.animation_running and self.mode_var.get() == "automatic":
                        break
                    progress = (i + 1) / steps
                    for arrow in arrows_to_draw:
                        current_x = arrow['start'][0] + (arrow['end'][0] - arrow['start'][0]) * progress
                        current_y = arrow['start'][1] + (arrow['end'][1] - arrow['start'][1]) * progress
                        self.canvas.coords(arrow['id'],
                                           arrow['start'][0], arrow['start'][1],
                                           current_x, current_y)
                    self.canvas.update()
                    time.sleep(duration / steps)

            else:
                # Remove root connections with animation
                arrows_to_remove = []
                for conn in step['connections']:
                    arrow_key = f"root-{conn['node']}"
                    if arrow_key in self.arrows:
                        arrow_id = self.arrows[arrow_key]
                        coords = self.canvas.coords(arrow_id)
                        arrows_to_remove.append({
                            'id': arrow_id,
                            'start': (coords[0], coords[1]),
                            'end': (coords[2], coords[3])
                        })

                steps = 20
                for i in range(steps - 1, -1, -1):
                    progress = i / steps
                    for arrow in arrows_to_remove:
                        current_x = arrow['start'][0] + (arrow['end'][0] - arrow['start'][0]) * progress
                        current_y = arrow['start'][1] + (arrow['end'][1] - arrow['start'][1]) * progress
                        self.canvas.coords(arrow['id'],
                                           arrow['start'][0], arrow['start'][1],
                                           current_x, current_y)
                    self.canvas.update()
                    time.sleep(duration / steps)

                # Delete arrows
                for conn in step['connections']:
                    arrow_key = f"root-{conn['node']}"
                    if arrow_key in self.arrows:
                        self.canvas.delete(self.arrows[arrow_key])
                        del self.arrows[arrow_key]

                # Remove root node
                if hasattr(self, 'root_node'):
                    self.animate_node_removal(self.root_node, duration)
                    for item in self.root_node:
                        self.canvas.delete(item)
                    delattr(self, 'root_node')

    def animate_node_removal(self, node_ids, duration):
        """Animate node disappearance with proper scaling"""
        node_id, text_id, index_id = node_ids
        steps = 20

        # Get original coordinates
        coords = self.canvas.coords(node_id)
        center_x = (coords[0] + coords[2]) / 2
        center_y = (coords[1] + coords[3]) / 2
        original_radius = (coords[2] - coords[0]) / 2

        # Hide text and index
        self.canvas.itemconfig(text_id, state='hidden')
        self.canvas.itemconfig(index_id, state='hidden')

        # Shrink circle
        for i in range(steps - 1, -1, -1):
            if not self.animation_running and self.mode_var.get() == "automatic":
                break
            current_r = (i + 1) * original_radius / steps
            self.canvas.coords(node_id,
                               center_x - current_r, center_y - current_r,
                               center_x + current_r, center_y + current_r)
            self.canvas.update()
            time.sleep(duration / steps)

    def animate_node(self, x, y, value, index, duration, scale, force_draw=False):
        """Animate node appearance with scaling including line thickness"""
        x *= scale
        y *= scale
        node_line_width = self.calculate_node_properties()

        node_id = self.canvas.create_oval(
            x, y, x, y,
            fill="lightblue",
            width=node_line_width
        )
        text_id = self.canvas.create_text(
            x, y,
            text=str(value),
            font=("Arial", round(12 * scale)),
            state='hidden'
        )
        index_id = self.canvas.create_text(
            x, y - 30 * scale,
            text=str(index),
            font=("Arial", round(12 * scale)),
            state='hidden'
        )

        r = 15 * scale
        if force_draw:
            # Draw immediately without animation
            self.canvas.coords(node_id,
                               x - r, y - r,
                               x + r, y + r)
            self.canvas.itemconfig(text_id, state='normal')
            self.canvas.itemconfig(index_id, state='normal')
        else:
            # Animate as before
            steps = 20
            for i in range(steps):
                if not self.animation_running and self.mode_var.get() == "automatic" and not force_draw:
                    break
                current_r = (i + 1) * r / steps
                self.canvas.coords(node_id,
                                   x - current_r, y - current_r,
                                   x + current_r, y + current_r)
                self.canvas.update()
                time.sleep(duration / steps)

            self.canvas.itemconfig(text_id, state='normal')
            self.canvas.itemconfig(index_id, state='normal')

        return node_id, text_id, index_id

    def calculate_arrow_properties(self):
        """Calculate arrow line width and shape based on current scale."""
        scale_value = self.scale_value.get()
        scale_factor = self.application.scale_factor
        scale = scale_value * scale_factor

        base_arrow_line_width = 3
        arrow_head_length = 12
        base_to_tip_distance = 12
        half_width_at_base = 4

        arrow_line_width = max(base_arrow_line_width, round(base_arrow_line_width * scale))
        d1 = max(arrow_head_length, int(arrow_head_length * scale))
        d2 = max(base_to_tip_distance, int(base_to_tip_distance * scale))
        d3 = max(half_width_at_base, int(half_width_at_base * scale))
        arrow_shape = (d1, d2, d3)
        return arrow_line_width, arrow_shape

    def calculate_node_properties(self):
        """Calculate node border width based on current scale"""
        scale_value = self.scale_value.get()
        scale_factor = self.application.scale_factor
        scale = scale_value * scale_factor

        base_node_line_width = 3

        node_line_width = max(base_node_line_width, round(base_node_line_width * scale))
        return node_line_width

    def calculate_rectangle_properties(self):
        """Calculate rectangle border width and size based on current scale"""
        scale_value = self.scale_value.get()
        scale_factor = self.application.scale_factor
        scale = scale_value * scale_factor

        base_rect_line_width = 2

        rect_line_width = max(base_rect_line_width, round(base_rect_line_width * scale))
        return rect_line_width


    def start_animation(self):
        """Start or resume animation"""
        if not self.initialized or self.step_in_progress:
            return

        self.animation_running = True
        self.paused = False
        self.input_entry.config(state='disabled')
        self.init_button.config(state='disabled')
        self.update_scroll_region()
        self.update_controls()

        if self.mode_var.get() == "automatic":
            self.animation_thread = threading.Thread(target=self.run_animation)
            self.animation_thread.start()

    def stop_animation(self):
        """Stop animation after current step completes"""
        if not self.animation_running:
            return

        self.paused = True
        self.update_controls()
        self.update_controls()

    def run_animation(self):
        """Run automatic animation with proper cleanup"""
        try:
            while (self.animation_running and
                   self.current_step < len(self.animation_steps) and
                   not self.is_cleaning_up):  # Add cleanup check
                if self.paused:
                    time.sleep(0.1)
                    continue

                self.step_in_progress = True
                try:
                    self.execute_step(self.animation_steps[self.current_step])
                except tk.TclError:
                    # Canvas was destroyed, exit the animation
                    break
                self.current_step += 1
                self.step_in_progress = False

                if self.current_step < len(self.animation_steps):
                    time.sleep(0.2 / self.speed_scale.get())

                if self.paused:
                    self.animation_running = False
                    break
        finally:
            self.animation_running = False
            self.step_in_progress = False
            self.paused = False
            if not self.is_cleaning_up:  # Only update controls if not cleaning up
                self.parent.after(0, self.update_controls)

    def next_step(self):
        """Execute next animation step in manual mode"""
        if (not self.initialized or self.step_in_progress or
                self.current_step >= len(self.animation_steps) or
                self.is_cleaning_up):  # Add cleanup check
            return

        self.step_in_progress = True
        try:
            self.update_scroll_region()
            self.update_controls()
            self.execute_step(self.animation_steps[self.current_step])
            self.current_step += 1
        except tk.TclError:
            # Canvas was destroyed, ignore the error
            pass
        finally:
            self.step_in_progress = False
            if not self.is_cleaning_up:  # Only update if not cleaning up
                self.update_scroll_region()
                self.update_controls()

    def prev_step(self):
        """Execute previous animation step in manual mode"""
        if (not self.initialized or self.step_in_progress or
                self.current_step <= 0 or
                self.is_cleaning_up):  # Add cleanup check
            return

        self.step_in_progress = True
        try:
            self.current_step -= 1
            self.update_scroll_region()
            self.update_controls()
            self.execute_step(self.animation_steps[self.current_step], reverse=True)
        except tk.TclError:
            # Canvas was destroyed, ignore the error
            pass
        finally:
            self.step_in_progress = False
            if not self.is_cleaning_up:  # Only update if not cleaning up
                self.update_scroll_region()
                self.update_controls()


    def mode_changed(self):
        """Handle mode change"""
        if self.animation_running:
            return

        self.update_scroll_region()
        self.update_controls()

    def scale_changed(self, value):
        """Handle scale change and update diagram instantly"""
        if not self.initialized:
            return

        try:
            # Clear current state
            self.canvas.delete('all')
            self.nodes.clear()
            self.arrows.clear()

            self.prepare_animation_steps(is_loaded_from_file=True)

            # Redraw initial state with scaled positions
            self.draw_initial_state()

            # Redraw all steps up to the current step with correct positions
            for step in self.animation_steps[:self.current_step]:
                self.instant_draw_step(step)

            # Update any necessary UI elements
            self.divide_positions_by_scale()
            self.update_controls()
            self.update_scroll_region()

        except Exception as e:
            print(f"Error during scaling: {e}")

    def update_scroll_region(self):
        """Update scroll region with proper padding"""
        bbox = self.canvas.bbox("all")
        if bbox is not None:
            bbox = list(bbox)
            if bbox:
                # Add padding to the scroll region
                if hasattr(self.application, 'is_fullscreen') and self.application.is_fullscreen:
                    # Use smaller padding in fullscreen mode to maintain margins
                    padding_ratio = 0.1
                else:
                    padding_ratio = 0.1  # 10% padding in normal mode

                window_width = self.canvas.winfo_width()
                window_height = self.canvas.winfo_height()
                print(f"Window size: {window_width}x{window_height}")

                # Ensure scroll region covers at least the window size
                bbox[2] = max(bbox[2] * (1 + padding_ratio), window_width)
                bbox[3] = max(bbox[3] * (1 + padding_ratio), window_height)

                self.canvas.configure(scrollregion=bbox)

    def update_controls(self):
        """Update control states"""
        try:
            if self.is_cleaning_up:
                return

            is_automatic = self.mode_var.get() == "automatic"
            is_running = self.animation_running
            step_active = self.step_in_progress
            animation_complete = self.initialized and self.current_step >= len(self.animation_steps)

            # During animation, disable all controls except stop, speed, and close buttons
            if is_running or step_active:
                # Disable most controls
                if hasattr(self, 'auto_radio'):
                    self.auto_radio.config(state='disabled')
                if hasattr(self, 'manual_radio'):
                    self.manual_radio.config(state='disabled')
                if hasattr(self, 'load_button'):
                    self.load_button.config(state='disabled')
                if hasattr(self, 'save_button'):
                    self.save_button.config(state='disabled')
                if hasattr(self, 'init_button'):
                    self.init_button.config(state='disabled')
                if hasattr(self, 'input_entry'):
                    self.input_entry.config(state='disabled')
                if hasattr(self, 'scale_slider'):
                    self.scale_slider.config(state='disabled')
                if hasattr(self, 'back_button'):
                    self.back_button.config(state='normal')

                # Configure mode-specific buttons
                if is_automatic:
                    # Pack Start/Stop buttons to fill the space
                    if hasattr(self, 'start_button'):
                        self.start_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                        self.start_button.config(state='disabled')
                    if hasattr(self, 'stop_button'):
                        self.stop_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                        self.stop_button.config(state='normal')
                    if hasattr(self, 'prev_button'):
                        self.prev_button.pack_forget()
                    if hasattr(self, 'next_button'):
                        self.next_button.pack_forget()
                else:
                    # Pack Previous/Next buttons to fill the space
                    if hasattr(self, 'start_button'):
                        self.start_button.pack_forget()
                    if hasattr(self, 'stop_button'):
                        self.stop_button.pack_forget()
                    if hasattr(self, 'prev_button'):
                        self.prev_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                        self.prev_button.config(state='disabled')
                    if hasattr(self, 'next_button'):
                        self.next_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                        self.next_button.config(state='disabled')
                return

            # When not animating, enable appropriate controls
            if hasattr(self, 'auto_radio'):
                self.auto_radio.config(state='normal')
            if hasattr(self, 'manual_radio'):
                self.manual_radio.config(state='normal')
            if hasattr(self, 'input_entry'):
                self.input_entry.config(state='normal')
            if hasattr(self, 'init_button'):
                self.init_button.config(state='normal')
            if hasattr(self, 'load_button'):
                self.load_button.config(state='normal')
            if hasattr(self, 'scale_slider'):
                self.scale_slider.config(state='normal')
            if hasattr(self, 'save_button'):
                self.save_button.config(state='normal' if self.initialized else 'disabled')
            if hasattr(self, 'back_button'):
                self.back_button.config(state='normal')

            # Update mode-specific controls
            if is_automatic:
                # Pack Start/Stop buttons to fill the space
                if hasattr(self, 'start_button'):
                    self.start_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    self.start_button.config(
                        state='normal' if self.initialized and not animation_complete else 'disabled')
                if hasattr(self, 'stop_button'):
                    self.stop_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    self.stop_button.config(state='disabled')
                if hasattr(self, 'prev_button'):
                    self.prev_button.pack_forget()
                if hasattr(self, 'next_button'):
                    self.next_button.pack_forget()
            else:
                # Pack Previous/Next buttons to fill the space
                if hasattr(self, 'start_button'):
                    self.start_button.pack_forget()
                if hasattr(self, 'stop_button'):
                    self.stop_button.pack_forget()
                if hasattr(self, 'prev_button'):
                    self.prev_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    self.prev_button.config(state='normal' if self.current_step > 0 else 'disabled')
                if hasattr(self, 'next_button'):
                    self.next_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
                    self.next_button.config(
                        state='normal' if self.current_step < len(self.animation_steps) else 'disabled')

        except tk.TclError:
            # Handle case where widgets are being destroyed
            pass
        except Exception as e:
            print(f"Error in update_controls: {e}")
            pass


    def calculate_levels(self, n):
        """Calculate levels for each node based on RSB"""
        levels = {}
        for i in range(1, n + 1):
            RSB = i & -i
            level = RSB.bit_length()
            if level not in levels:
                levels[level] = []
            levels[level].append(i)
        return levels

    def calculate_positions(self, n, levels, is_loaded_from_file=False):
        scale_value = self.scale_value.get()
        self_factor = self.application.scale_factor
        scale = scale_value * self_factor if is_loaded_from_file else 1

        positions = {}
        max_level = max(levels.keys())
        left_margin = 100 * scale
        top_margin = 80 * scale
        x_spacing = 50 * scale

        for level in sorted(levels.keys(), reverse=True):
            y = top_margin + (max_level - level) * 50 * scale
            for node in levels[level]:
                x = left_margin + node * x_spacing
                positions[node] = (x, y)
                print(f"Node {node} position: ({x}, {y})")

        return positions

    def calculate_root_position(self, positions, is_loaded_from_file=False):
        """Calculate position for root node"""
        scale_value = self.scale_value.get()
        self_factor = self.application.scale_factor
        scale = scale_value * self_factor if is_loaded_from_file else 1

        if not positions:
            return (0, 0)
        # Find highest node (minimum y value)
        min_y = min(y for x, y in positions.values())
        # Find rightmost node (maximum x value)
        max_x = max(x for x, y in positions.values())

        # Position root slightly above and to the right of highest nodes
        return (max_x + 70 * scale, min_y - 10 * scale)

    def find_parentless_nodes(self, n):
        """Find nodes that don't have parents in the tree"""
        parentless = set(range(1, n + 1))
        for i in range(1, n + 1):
            parent = i + (i & -i)
            if parent <= n:
                parentless.discard(i)
        return parentless


    def save_to_file(self):
        """Save complete diagram state"""
        if not self.initialized:
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not filename:
                return

            # Save complete state
            state = {
                'initial_array': self.initial_array,
                'bit_array': self.bit_array,
                'current_step': self.current_step
            }

            with open(filename, 'w') as f:
                json.dump(state, f)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def load_from_file(self):
        """Load state and rebuild diagram instantly"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if not filename:
                return

            with open(filename, 'r') as f:
                state = json.load(f)

            # Load and set initial array
            self.initial_array = state['initial_array']
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, ','.join(map(str, self.initial_array)))

            self.initialize_bit(state['current_step'])

            self.current_step = state['current_step']
            self.initialized = True
            self.scale_changed("placeholder")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def instant_draw_step(self, step):
        """Draw step instantly without animation"""
        scale_value = self.scale_value.get()
        self_factor = self.application.scale_factor
        scale = scale_value * self_factor

        node_line_width = self.calculate_node_properties()
        arrow_line_width, arrow_shape = self.calculate_arrow_properties()   # Scale arrow shape and width

        if step['type'] == 'leaf_node':
            node = step['node']
            x, y = node['position']
            r = 15 * scale

            # Create node instantly with scaled line width
            node_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="lightblue",
                width=node_line_width
            )
            text_id = self.canvas.create_text(
                x, y,
                text=str(node['value']),
                font=("Arial", round(12 * scale))
            )
            index_id = self.canvas.create_text(
                x, y - 30 * scale,
                text=str(node['index']),
                font=("Arial", round(12 * scale))
            )
            self.nodes[node['index']] = (node_id, text_id, index_id)

        elif step['type'] == 'parent_with_children':
            # Create parent node instantly with scaled line width
            parent = step['parent']
            x, y = parent['position']
            r = 15 * scale

            node_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="lightblue",
                width=node_line_width
            )
            text_id = self.canvas.create_text(
                x, y,
                text=str(step['final_value']),
                font=("Arial", round(12 * scale))
            )
            index_id = self.canvas.create_text(
                x, y - 30 * scale,
                text=str(parent['index']),
                font=("Arial", round(12 * scale))
            )
            self.nodes[parent['index']] = (node_id, text_id, index_id)

            # Draw all arrows instantly with proper intersections
            for child in step['children']:
                child_pos = child['position']

                # Calculate both intersection points
                end_x, end_y = self.calculate_arrow_intersection(
                    x, y, child_pos[0], child_pos[1], r, is_loaded_from_file=True)
                start_x, start_y = self.calculate_arrow_intersection(
                    child_pos[0], child_pos[1], x, y, r, is_loaded_from_file=True)

                # Draw arrows with scaled line width
                arrow_id = self.canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    arrow=tk.LAST,
                    width=arrow_line_width,
                    arrowshape=arrow_shape,
                )
                self.arrows[f"{parent['index']}-{child['index']}"] = arrow_id

        elif step['type'] == 'root_with_connections':
            # Draw root node instantly
            x, y = step['position']
            r = 15 * scale

            node_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="lightblue",
                width=node_line_width
            )
            text_id = self.canvas.create_text(
                x, y,
                text='R',
                font=("Arial", round(12 * scale))
            )
            index_id = self.canvas.create_text(
                x, y - 30 * scale,
                text='R',
                font=("Arial", round(12 * scale))
            )
            self.root_node = (node_id, text_id, index_id)

            # Draw all connections instantly with proper intersections
            for conn in step['connections']:
                end_x, end_y = self.calculate_arrow_intersection(
                    x, y, conn['position'][0], conn['position'][1], r, is_loaded_from_file=True)
                start_x, start_y = self.calculate_arrow_intersection(
                    conn['position'][0], conn['position'][1], x, y, r, is_loaded_from_file=True)

                # Draw arrows with scaled line width
                arrow_id = self.canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    arrow=tk.LAST,
                    width=arrow_line_width,
                    arrowshape=arrow_shape,
                )
                self.arrows[f"root-{conn['node']}"] = arrow_id

    def divide_positions_by_scale(self):
        """Divide positions by scale and assign back to animation steps"""
        scale_value = self.scale_value.get()
        self_factor = self.application.scale_factor
        scale = scale_value * self_factor

        # Go through all animation steps
        for step in self.animation_steps:
            if step['type'] == 'leaf_node':
                # Normalize leaf node position
                x, y = step['node']['position']
                step['node']['position'] = (x / scale, y / scale)

            elif step['type'] == 'parent_with_children':
                # Normalize parent node position
                x, y = step['parent']['position']
                step['parent']['position'] = (x / scale, y / scale)

                # Normalize children positions
                for child in step['children']:
                    x, y = child['position']
                    child['position'] = (x / scale, y / scale)

            elif step['type'] == 'root_with_connections':
                # Normalize root position
                x, y = step['position']
                step['position'] = (x / scale, y / scale)

                # Normalize connected nodes positions
                for conn in step['connections']:
                    x, y = conn['position']
                    conn['position'] = (x / scale, y / scale)

# Run application
if __name__ == "__main__":
    app = MainApplication()
    app.run()