import tkinter as tk
from tkinter import ttk
from ..utils.constants import DEFAULT_FONT, TITLE_FONT_SIZE, HEADING_FONT_SIZE


class MenuManager:
    def __init__(self, parent, callback_handler):
        self.parent = parent
        self.callbacks = callback_handler

    def create_main_menu(self):
        """Create enhanced main menu with modern styling"""
        menu_frame = ttk.Frame(self.parent)
        menu_frame.grid(row=1, column=0, sticky="nsew")
        menu_frame.grid_rowconfigure(0, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)

        # Create centered content frame
        content_frame = ttk.Frame(menu_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title = ttk.Label(
            content_frame,
            text="Binary Indexed Tree Visualizer",
            style='Title.TLabel'
        )
        title.pack(pady=(0, 40))

        # Create button container
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Create buttons
        build_button = ttk.Button(
            buttons_frame,
            text="Build BIT",
            command=self.callbacks.open_bit_builder,
            style='Menu.TButton',
            width=30
        )
        build_button.pack(pady=20, fill=tk.X)

        desc_button = ttk.Button(
            buttons_frame,
            text="Algorithm Description",
            command=self.callbacks.show_algorithm_description,
            style='Menu.TButton',
            width=30
        )
        desc_button.pack(pady=20, fill=tk.X)

        guide_button = ttk.Button(
            buttons_frame,
            text="Interface Guide",
            command=self.callbacks.show_interface_guide,
            style='Menu.TButton',
            width=30
        )
        guide_button.pack(pady=20, fill=tk.X)

        return menu_frame

    def update_text_scaling(self, event, text_widget, title_widget, scale_factor):
        """Update text scaling when window size changes"""
        if event.widget == self.parent:
            try:
                # Update font sizes
                title_size = round(TITLE_FONT_SIZE * scale_factor)
                heading_size = round(HEADING_FONT_SIZE * scale_factor)
                text_size = round(12 * scale_factor)

                # Update text widget fonts
                text_widget.tag_configure('heading', font=(DEFAULT_FONT, heading_size, 'bold'))
                text_widget.tag_configure('normal', font=(DEFAULT_FONT, text_size))
                text_widget.tag_configure('bullet', font=(DEFAULT_FONT, text_size))
                title_widget.configure(font=(DEFAULT_FONT, title_size, 'bold'))
            except tk.TclError:
                pass

    def show_algorithm_description(self):
        """Show algorithm description window with text scaling"""
        description_text = """# Overview
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
3. Simple Implementation: Easier to code than other similar data structures"""

        self._show_text_window("Binary Indexed Tree (BIT)", description_text)

    def show_interface_guide(self):
        """Show interface guide window with text scaling"""
        guide_text = """# Building BIT
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
• Close application (✕ button)"""

        self._show_text_window("Interface Guide", guide_text)

    def _show_text_window(self, title, content):
        """Helper method to show text windows with consistent styling"""
        # Create and configure the window
        text_frame = ttk.Frame(self.parent)
        text_frame.grid(row=1, column=0, sticky="nsew")

        content_frame = ttk.Frame(text_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Add back button
        back_button = ttk.Button(
            content_frame,
            text="← Back to Menu",
            command=lambda: self.callbacks.return_to_menu(text_frame),
            style='Custom.TButton'
        )
        back_button.pack(pady=(5, 15), anchor='w')

        # Add title
        title_widget = ttk.Label(
            content_frame,
            text=title,
            font=(DEFAULT_FONT, TITLE_FONT_SIZE, 'bold')
        )
        title_widget.pack(pady=(0, 20))

        # Create text container
        text_container = ttk.Frame(content_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        # Create text widget
        text_widget = tk.Text(
            text_container,
            wrap=tk.WORD,
            padx=20,
            pady=20,
            font=(DEFAULT_FONT, 12),
            bg='#f5f5f5'
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Configure text tags
        text_widget.tag_configure('heading', font=(DEFAULT_FONT, HEADING_FONT_SIZE, 'bold'))
        text_widget.tag_configure('normal', font=(DEFAULT_FONT, 12))
        text_widget.tag_configure('bullet', font=(DEFAULT_FONT, 12))

        # Insert text with formatting
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                text_widget.insert(tk.END, line[2:] + '\n', 'heading')
            elif line.startswith('• '):
                text_widget.insert(tk.END, line + '\n', 'bullet')
            else:
                text_widget.insert(tk.END, line + '\n', 'normal')

        text_widget.configure(state='disabled')

        return text_widget, title_widget