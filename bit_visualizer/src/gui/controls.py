import tkinter as tk
from tkinter import ttk


class ControlPanel:
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.control_panel = ttk.Frame(parent)
        self.control_panel.pack(fill=tk.X, padx=5, pady=5)

        # Calculate paddings and sizes based on scale factor
        scale_factor = self.callbacks['get_scale_factor']()
        base_padding = round(5 * scale_factor)
        frame_padding = round(10 * scale_factor)

        # Back to Menu button
        back_frame = ttk.Frame(self.control_panel)
        back_frame.pack(fill=tk.X, pady=(0, base_padding))

        self.back_button = ttk.Button(
            back_frame,
            text="← Back to Menu",
            command=self.callbacks['back_to_menu'],
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

        self.load_button = ttk.Button(
            file_buttons,
            text="Load",
            command=self.callbacks['load_from_file'],
            style='Control.TButton'
        )
        self.load_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

        self.save_button = ttk.Button(
            file_buttons,
            text="Save",
            command=self.callbacks['save_to_file'],
            style='Control.TButton'
        )
        self.save_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

        # Input section
        self.input_frame = ttk.LabelFrame(
            self.control_panel,
            text="Input",
            style='Custom.TLabelframe'
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
            command=self.callbacks['initialize_bit'],
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

        # Mode selection
        mode_frame = ttk.Frame(self.anim_frame)
        mode_frame.pack(fill=tk.X, expand=True)

        self.mode_var = tk.StringVar(value="automatic")
        self.auto_radio = ttk.Radiobutton(
            mode_frame,
            text="Automatic",
            variable=self.mode_var,
            value="automatic",
            command=self.callbacks['mode_changed'],
            style='Custom.TRadiobutton'
        )
        self.manual_radio = ttk.Radiobutton(
            mode_frame,
            text="Manual",
            variable=self.mode_var,
            value="manual",
            command=self.callbacks['mode_changed'],
            style='Custom.TRadiobutton'
        )

        self.auto_radio.pack(side=tk.LEFT, expand=True)
        self.manual_radio.pack(side=tk.LEFT, expand=True)

        # Control buttons
        self.button_frame = ttk.Frame(self.anim_frame)
        self.button_frame.pack(fill=tk.X, pady=base_padding)

        self.start_button = ttk.Button(
            self.button_frame,
            text="Start",
            command=self.callbacks['start_animation'],
            style='Control.TButton'
        )
        self.stop_button = ttk.Button(
            self.button_frame,
            text="Stop",
            command=self.callbacks['stop_animation'],
            style='Control.TButton'
        )
        self.prev_button = ttk.Button(
            self.button_frame,
            text="Previous",
            command=self.callbacks['prev_step'],
            style='Control.TButton'
        )
        self.next_button = ttk.Button(
            self.button_frame,
            text="Next",
            command=self.callbacks['next_step'],
            style='Control.TButton'
        )

        # Sliders frame
        slider_frame = ttk.Frame(self.anim_frame)
        slider_frame.pack(fill=tk.X, pady=base_padding)

        # Scale control
        scale_frame = ttk.Frame(slider_frame)
        scale_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)
        ttk.Label(scale_frame, text="Scale:", style='Custom.TLabelframe.Label').pack(side=tk.LEFT)

        self.scale_value = tk.DoubleVar(value=1.0)
        self.scale_slider = ttk.Scale(
            scale_frame,
            from_=0.5, to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.scale_value,
            command=self.callbacks['scale_changed'],
            style='Custom.Horizontal.TScale'
        )
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

        # Speed control
        speed_frame = ttk.Frame(slider_frame)
        speed_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)
        ttk.Label(speed_frame, text="Speed:", style='Custom.TLabelframe.Label').pack(side=tk.LEFT)

        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=1, to=10.0,
            orient=tk.HORIZONTAL,
            style='Custom.Horizontal.TScale'
        )
        self.speed_scale.set(3.0)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=base_padding)

    def get_mode(self):
        return self.mode_var.get()

    def get_speed(self):
        return self.speed_scale.get()

    def get_scale_value(self):
        return self.scale_value.get()

    def update_controls(self, is_automatic, is_running, step_active, animation_complete, initialized, current_step,
                        total_steps):
        """Update control states based on current application state"""
        try:
            if is_running or step_active:
                # Disable most controls during animation
                self.auto_radio.config(state='disabled')
                self.manual_radio.config(state='disabled')
                self.load_button.config(state='disabled')
                self.save_button.config(state='disabled')
                self.init_button.config(state='disabled')
                self.input_entry.config(state='disabled')
                self.scale_slider.config(state='disabled')
                self.back_button.config(state='normal')

                if is_automatic:
                    self._configure_automatic_mode(True)
                else:
                    self._configure_manual_mode(True)
                return

            # When not animating, enable appropriate controls
            self._enable_basic_controls(initialized)

            if is_automatic:
                self._configure_automatic_mode(False, initialized, animation_complete)
            else:
                self._configure_manual_mode(False, current_step, total_steps)

        except tk.TclError:
            # Handle case where widgets are being destroyed
            pass

    def _enable_basic_controls(self, initialized):
        """Enable basic controls"""
        self.auto_radio.config(state='normal')
        self.manual_radio.config(state='normal')
        self.input_entry.config(state='normal')
        self.init_button.config(state='normal')
        self.load_button.config(state='normal')
        self.scale_slider.config(state='normal')
        self.save_button.config(state='normal' if initialized else 'disabled')
        self.back_button.config(state='normal')

    def _configure_automatic_mode(self, is_running, initialized=False, animation_complete=False):
        """Configure controls for automatic mode"""
        self.start_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.stop_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.prev_button.pack_forget()
        self.next_button.pack_forget()

        if is_running:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
        else:
            self.start_button.config(state='normal' if initialized and not animation_complete else 'disabled')
            self.stop_button.config(state='disabled')

    def _configure_manual_mode(self, is_running, current_step=0, total_steps=0):
        """Configure controls for manual mode"""
        self.start_button.pack_forget()
        self.stop_button.pack_forget()
        self.prev_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.next_button.pack(in_=self.button_frame, side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        if is_running:
            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')
        else:
            self.prev_button.config(state='normal' if current_step > 0 else 'disabled')
            self.next_button.config(state='normal' if current_step < total_steps else 'disabled')