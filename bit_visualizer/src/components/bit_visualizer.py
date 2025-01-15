import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

from ..utils.geometry import calculate_positions, calculate_root_position, calculate_arrow_intersection, calculate_visual_properties
from ..utils.constants import (NODE_RADIUS, NODE_COLOR, DEFAULT_FONT, DEFAULT_FONT_SIZE,
                             ANIMATION_STEPS, LEFT_MARGIN, TOP_MARGIN, X_SPACING)
from ..core.bit_operations import calculate_bit_array, calculate_levels
from ..core.animation import prepare_animation_steps
from ..core.file_operations import save_state, load_state
from ..gui.controls import ControlPanel


class BITVisualizer:
    def __init__(self, parent, application):
        """Initialize BIT visualizer"""
        self.parent = parent
        self.is_cleaning_up = False
        self.application = application

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

        # Create control panel with callbacks
        callbacks = {
            'get_scale_factor': lambda: self.application.scale_factor,
            'back_to_menu': lambda: self.application.return_to_menu(self.parent),
            'load_from_file': self.load_from_file,
            'save_to_file': self.save_to_file,
            'initialize_bit': self.initialize_bit,
            'mode_changed': self.mode_changed,
            'start_animation': self.start_animation,
            'stop_animation': self.stop_animation,
            'prev_step': self.prev_step,
            'next_step': self.next_step,
            'scale_changed': self.scale_changed
        }
        self.control_panel = ControlPanel(parent, callbacks)

        # Canvas setup with scrollbars and adaptability
        self.canvas_frame = ttk.Frame(parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Canvas creation
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
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

        # Initialize controls
        self.update_controls()

    def create_control_components(self):
        """Create control panel components"""
        # Back button
        self.back_button = ttk.Button(
            self.control_panel,
            text="← Back to Menu",
            command=lambda: self.application.return_to_menu(self.parent),
            style='Custom.TButton'
        )
        self.back_button.pack(pady=(5, 15), anchor='w')

        # File operations frame
        self.file_frame = ttk.LabelFrame(
            self.control_panel,
            text="File Operations",
            style='Custom.TLabelframe'
        )
        self.file_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)

        self.load_button = ttk.Button(
            self.file_frame,
            text="Load",
            command=self.load_from_file,
            style='Control.TButton'
        )
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(
            self.file_frame,
            text="Save",
            command=self.save_to_file,
            style='Control.TButton'
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Input frame
        self.input_frame = ttk.LabelFrame(
            self.control_panel,
            text="Input",
            style='Custom.TLabelframe'
        )
        self.input_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

        self.input_label = ttk.Label(
            self.input_frame,
            text="Array:",
            style='Custom.TLabelframe.Label'
        )
        self.input_label.pack(side=tk.LEFT, padx=5)

        self.input_entry = ttk.Entry(
            self.input_frame,
            style='Custom.TEntry'
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.init_button = ttk.Button(
            self.input_frame,
            text="Initialize",
            command=self.initialize_bit,
            style='Control.TButton'
        )
        self.init_button.pack(side=tk.LEFT, padx=5)

        # Animation controls frame
        self.anim_frame = ttk.LabelFrame(
            self.control_panel,
            text="Animation Controls",
            style='Custom.TLabelframe'
        )
        self.anim_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)

        # Mode selection
        self.mode_var = tk.StringVar(value="automatic")
        self.auto_radio = ttk.Radiobutton(
            self.anim_frame,
            text="Automatic",
            variable=self.mode_var,
            value="automatic",
            command=self.mode_changed,
            style='Custom.TRadiobutton'
        )
        self.manual_radio = ttk.Radiobutton(
            self.anim_frame,
            text="Manual",
            variable=self.mode_var,
            value="manual",
            command=self.mode_changed,
            style='Custom.TRadiobutton'
        )

        self.auto_radio.pack(side=tk.LEFT)
        self.manual_radio.pack(side=tk.LEFT)

        # Control buttons
        self.button_frame = ttk.Frame(self.anim_frame)
        self.button_frame.pack(fill=tk.X, pady=5)

        self.start_button = ttk.Button(
            self.button_frame,
            text="Start",
            command=self.start_animation,
            style='Control.TButton'
        )

        self.stop_button = ttk.Button(
            self.button_frame,
            text="Stop",
            command=self.stop_animation,
            style='Control.TButton'
        )

        self.prev_button = ttk.Button(
            self.button_frame,
            text="Previous",
            command=self.prev_step,
            style='Control.TButton'
        )

        self.next_button = ttk.Button(
            self.button_frame,
            text="Next",
            command=self.next_step,
            style='Control.TButton'
        )

        # Scale and speed controls
        control_frame = ttk.Frame(self.anim_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Scale control
        scale_frame = ttk.Frame(control_frame)
        scale_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(scale_frame, text="Scale:", style='Custom.TLabelframe.Label').pack(side=tk.LEFT)

        self.scale_value = tk.DoubleVar(value=1.0)
        self.scale_slider = ttk.Scale(
            scale_frame,
            from_=0.5,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.scale_value,
            command=self.scale_changed,
            style='Custom.Horizontal.TScale'
        )
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(speed_frame, text="Speed:", style='Custom.TLabelframe.Label').pack(side=tk.LEFT)

        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=1,
            to=10.0,
            orient=tk.HORIZONTAL,
            style='Custom.Horizontal.TScale'
        )
        self.speed_scale.set(3.0)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def setup_canvas(self):
        """Set up canvas with scrollbars"""
        self.canvas_frame = ttk.Frame(self.parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
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

    def initialize_bit(self, current_step=0):
        """Initialize BIT structure"""
        if self.animation_running or self.step_in_progress:
            return

        try:
            self.initial_array = list(map(int, self.control_panel.input_entry.get().split(',')))
            self.bit_array = calculate_bit_array(self.initial_array)
            self.current_step = current_step
            self.initialized = True

            # Prepare animation steps
            levels = calculate_levels(len(self.initial_array))
            self.animation_steps = prepare_animation_steps(self.initial_array, self.bit_array, levels)

            # Draw initial state
            self.scale_changed("placeholder")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid comma-separated numbers")

    def draw_initial_state(self):
        """Draw static elements of visualization"""
        self.canvas.delete('all')
        scale = self.control_panel.get_scale_value() * self.application.scale_factor

        # Calculate visual properties
        visual_props = calculate_visual_properties(scale)

        # Draw array elements
        self.draw_arrays(scale, visual_props['rect_line_width'])

        # Draw RSB labels
        self.draw_rsb_labels(scale)

    def draw_arrays(self, scale, line_width):
        """Draw initial and BIT arrays"""
        x_spacing = X_SPACING * scale
        left_margin = LEFT_MARGIN * scale
        array_y = self._calculate_array_y_position(scale)
        box_size = NODE_RADIUS * scale

        # Draw arrays and labels
        for i in range(len(self.initial_array)):
            x = left_margin + (i + 1) * x_spacing
            self._draw_array_element(x, array_y, str(i + 1), scale)  # Index
            self._draw_array_element(x, array_y + 30 * scale, str(self.bit_array[i + 1]),
                                     scale, line_width)  # BIT array
            self._draw_array_element(x, array_y + 60 * scale, str(self.initial_array[i]),
                                     scale, line_width)  # Initial array

    def _draw_array_element(self, x, y, value, scale, line_width=1):
        """Draw single array element"""
        box_size = NODE_RADIUS * scale
        self.canvas.create_rectangle(
            x - box_size, y - box_size,
            x + box_size, y + box_size,
            outline="black",
            width=line_width
        )
        self.canvas.create_text(
            x, y,
            text=value,
            font=(DEFAULT_FONT, round(DEFAULT_FONT_SIZE * scale))
        )

    def draw_rsb_labels(self, scale):
        """Draw RSB labels"""
        levels = calculate_levels(len(self.initial_array))
        margin = TOP_MARGIN * scale

        # Draw header
        self.canvas.create_text(
            margin, margin,
            text="RSB",
            font=(DEFAULT_FONT, round(DEFAULT_FONT_SIZE * scale), "bold"),
            anchor="w"
        )

        # Draw RSB values
        max_level = max(levels.keys())
        for level in sorted(levels.keys(), reverse=True):
            y = margin + (max_level - level) * 50 * scale
            nodes_at_level = levels[level]
            rsb_value = nodes_at_level[0] & -nodes_at_level[0]
            self.canvas.create_text(
                margin, y + 50 * scale,
                text=str(rsb_value),
                font=(DEFAULT_FONT, round(DEFAULT_FONT_SIZE * scale), "bold"),
                anchor="w"
            )

    def _calculate_array_y_position(self, scale):
        """Calculate y position for array elements"""
        levels = calculate_levels(len(self.initial_array))
        max_level = max(levels.keys())
        return TOP_MARGIN * scale + (max_level + 1) * 50 * scale

    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self.parent:
            bbox = self.canvas.bbox("all")
            if bbox:
                bbox = list(bbox)
                width = self.parent.winfo_width()
                height = self.parent.winfo_height()

                bbox[2] = max(bbox[2], width)
                bbox[3] = max(bbox[3], height)

                padding_ratio = 0.1
                bbox[2] = bbox[2] * (1 + padding_ratio)
                bbox[3] = bbox[3] * (1 + padding_ratio)

                self.canvas.configure(scrollregion=bbox)

    def animate_node(self, x, y, value, index, duration, scale, force_draw=False):
        """Animate node appearance"""
        visual_props = calculate_visual_properties(scale)
        r = NODE_RADIUS * scale
        x *= scale
        y *= scale

        node_id = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=NODE_COLOR,
            width=visual_props['node_line_width']
        )

        text_id = self.canvas.create_text(
            x, y,
            text=str(value),
            font=(DEFAULT_FONT, round(DEFAULT_FONT_SIZE * scale)),
            state='hidden'
        )

        index_id = self.canvas.create_text(
            x, y - 30 * scale,
            text=str(index),
            font=(DEFAULT_FONT, round(DEFAULT_FONT_SIZE * scale)),
            state='hidden'
        )

        if not force_draw:
            self._animate_node_appearance(node_id, text_id, index_id, x, y, r, duration)
        else:
            self.canvas.itemconfig(text_id, state='normal')
            self.canvas.itemconfig(index_id, state='normal')

        return node_id, text_id, index_id

    def _animate_node_appearance(self, node_id, text_id, index_id, x, y, r, duration):
        """Animate node growing animation"""
        steps = ANIMATION_STEPS
        for i in range(steps):
            if not self.animation_running and self.control_panel.get_mode() == "automatic":
                break
            current_r = (i + 1) * r / steps
            self.canvas.coords(node_id,
                               x - current_r, y - current_r,
                               x + current_r, y + current_r)
            self.canvas.update()
            time.sleep(duration / steps)

        self.canvas.itemconfig(text_id, state='normal')
        self.canvas.itemconfig(index_id, state='normal')

    def animate_node_removal(self, node_ids, duration):
        """Animate node disappearance"""
        node_id, text_id, index_id = node_ids
        steps = ANIMATION_STEPS

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
            if not self.animation_running and self.control_panel.get_mode() == "automatic":
                break
            current_r = (i + 1) * original_radius / steps
            self.canvas.coords(node_id,
                               center_x - current_r, center_y - current_r,
                               center_x + current_r, center_y + current_r)
            self.canvas.update()
            time.sleep(duration / steps)

    def execute_step(self, step, reverse=False, force_draw=False):
        """Execute animation step"""
        scale = self.control_panel.get_scale_value() * self.application.scale_factor
        visual_props = calculate_visual_properties(scale)
        duration = 0 if force_draw else 1.0 / self.control_panel.get_speed()

        if step['type'] == 'leaf_node':
            self._execute_leaf_node_step(step, reverse, force_draw, scale, duration)
        elif step['type'] == 'parent_with_children':
            self._execute_parent_children_step(step, reverse, force_draw, scale, duration, visual_props)
        elif step['type'] == 'root_with_connections':
            self._execute_root_step(step, reverse, force_draw, scale, duration, visual_props)

    def update_controls(self):
        """Update control panel state"""
        self.control_panel.update_controls(
            is_automatic=self.control_panel.mode_var.get() == "automatic",
            is_running=self.animation_running,
            step_active=self.step_in_progress,
            animation_complete=self.initialized and self.current_step >= len(self.animation_steps),
            initialized=self.initialized,
            current_step=self.current_step,
            total_steps=len(self.animation_steps)
        )

    def start_animation(self):
        """Start animation"""
        if not self.initialized or self.step_in_progress:
            return

        self.animation_running = True
        self.paused = False
        self.update_controls()

        if self.control_panel.get_mode() == "automatic":
            self.animation_thread = threading.Thread(target=self.run_animation)
            self.animation_thread.start()

    def stop_animation(self):
        """Stop animation"""
        if not self.animation_running:
            return

        self.paused = True
        self.update_controls()

    def run_animation(self):
        """Run automatic animation"""
        try:
            while (self.animation_running and
                   self.current_step < len(self.animation_steps) and
                   not self.is_cleaning_up):
                if self.paused:
                    time.sleep(0.1)
                    continue

                self.step_in_progress = True
                try:
                    self.execute_step(self.animation_steps[self.current_step])
                except tk.TclError:
                    break

                self.current_step += 1
                self.step_in_progress = False

                if self.current_step < len(self.animation_steps):
                    time.sleep(0.2 / self.control_panel.get_speed())

                if self.paused:
                    self.animation_running = False
                    break
        finally:
            self.animation_running = False
            self.step_in_progress = False
            self.paused = False
            if not self.is_cleaning_up:
                self.parent.after(0, self.update_controls)

    def next_step(self):
        """Execute next step in manual mode"""
        if (not self.initialized or self.step_in_progress or
                self.current_step >= len(self.animation_steps) or
                self.is_cleaning_up):
            return

        self.step_in_progress = True
        try:
            self.execute_step(self.animation_steps[self.current_step])
            self.current_step += 1
        except tk.TclError:
            pass
        finally:
            self.step_in_progress = False
            if not self.is_cleaning_up:
                self.update_controls()

    def prev_step(self):
        """Execute previous step in manual mode"""
        if (not self.initialized or self.step_in_progress or
                self.current_step <= 0 or self.is_cleaning_up):
            return

        self.step_in_progress = True
        try:
            self.current_step -= 1
            self.execute_step(self.animation_steps[self.current_step], reverse=True)
        except tk.TclError:
            pass
        finally:
            self.step_in_progress = False
            if not self.is_cleaning_up:
                self.update_controls()

    def scale_changed(self, value):
        """Handle scale change"""
        if not self.initialized:
            return

        try:
            self.canvas.delete('all')
            self.nodes.clear()
            self.arrows.clear()

            # Recalculate animation steps
            levels = calculate_levels(len(self.initial_array))
            self.animation_steps = prepare_animation_steps(
                self.initial_array, self.bit_array, levels, is_loaded_from_file=True)

            # Redraw initial state
            self.draw_initial_state()

            # Redraw all steps up to current
            for step in self.animation_steps[:self.current_step]:
                self.execute_step(step, force_draw=True)

            self.update_controls()

        except Exception as e:
            print(f"Error during scaling: {e}")

    def mode_changed(self):
        """Handle animation mode change"""
        if self.animation_running:
            return
        self.update_controls()

    def save_to_file(self):
        """Save current state to file"""
        if not self.initialized:
            return

        success = save_state(
            initial_array=self.initial_array,
            bit_array=self.bit_array,
            current_step=self.current_step
        )

        if success:
            self.update_controls()

    def load_from_file(self):
        """Load state from file"""
        state = load_state()
        if not state:
            return

        # Update input field
        self.control_panel.input_entry.delete(0, tk.END)
        self.control_panel.input_entry.insert(0, ','.join(map(str, state['initial_array'])))

        # Initialize with loaded state
        self.initialize_bit(state['current_step'])
        self.current_step = state['current_step']
        self.initialized = True

        # Update visualization
        self.scale_changed("placeholder")

    def _execute_leaf_node_step(self, step, reverse, force_draw, scale, duration):
        """Execute leaf node animation step"""
        if not reverse:
            node = step['node']
            node_ids = self.animate_node(
                node['position'][0], node['position'][1],
                node['value'], node['index'],
                duration, scale, force_draw
            )
            self.nodes[node['index']] = node_ids
        else:
            if step['node']['index'] in self.nodes:
                node_ids = self.nodes[step['node']['index']]
                self.animate_node_removal(node_ids, duration)
                for item in node_ids:
                    self.canvas.delete(item)
                del self.nodes[step['node']['index']]

    def _execute_parent_children_step(self, step, reverse, force_draw, scale, duration, visual_props):
        """Execute parent-children animation step"""
        if not reverse:
            # Create parent node
            parent = step['parent']
            parent_pos = parent['position']
            node_ids = self.animate_node(
                parent_pos[0], parent_pos[1],
                parent['value'], parent['index'],
                duration, scale, force_draw
            )
            self.nodes[parent['index']] = node_ids

            # Draw arrows
            arrows_to_draw = []
            for child in step['children']:
                arrow_data = self._prepare_arrow(
                    parent_pos, child['position'],
                    parent['index'], child['index'],
                    scale, visual_props
                )
                arrows_to_draw.append(arrow_data)

            if not force_draw:
                self._animate_arrows(arrows_to_draw, duration)
                self._animate_value_transfers(step, scale, duration)

            # Update parent node value
            self.canvas.itemconfig(
                self.nodes[parent['index']][1],
                text=str(step['final_value'])
            )

        else:
            # Reverse animation logic...
            self._reverse_parent_children(step, duration)

    def _execute_root_step(self, step, reverse, force_draw, scale, duration, visual_props):
        """Execute root node animation step"""
        if not reverse:
            # Add root node
            x, y = step['position']
            self.root_node = self.animate_node(x, y, 'R', 'R', duration, scale, force_draw)

            # Add connections
            arrows_to_draw = []
            for conn in step['connections']:
                arrow_data = self._prepare_arrow(
                    (x, y), conn['position'],
                    'root', conn['node'],
                    scale, visual_props
                )
                arrows_to_draw.append(arrow_data)

            if not force_draw:
                self._animate_arrows(arrows_to_draw, duration)

        else:
            self._reverse_root_step(step, duration)

    def _prepare_arrow(self, start_pos, end_pos, from_id, to_id, scale, visual_props):
        """Prepare arrow data for animation"""
        r = NODE_RADIUS
        end_x, end_y = calculate_arrow_intersection(
            start_pos[0], start_pos[1],
            end_pos[0], end_pos[1],
            r, scale
        )
        start_x, start_y = calculate_arrow_intersection(
            end_pos[0], end_pos[1],
            start_pos[0], start_pos[1],
            r, scale
        )

        arrow_id = self.canvas.create_line(
            start_x, start_y, start_x, start_y,
            arrow=tk.LAST,
            width=visual_props['arrow_line_width'],
            arrowshape=visual_props['arrow_shape']
        )

        self.arrows[f"{from_id}-{to_id}"] = arrow_id

        return {
            'id': arrow_id,
            'start': (start_x, start_y),
            'end': (end_x, end_y),
        }

    def _animate_arrows(self, arrows_to_draw, duration):
        """Animate multiple arrows simultaneously"""
        steps = ANIMATION_STEPS
        for i in range(steps):
            if not self.animation_running and self.control_panel.get_mode() == "automatic":
                break

            progress = (i + 1) / steps
            for arrow in arrows_to_draw:
                current_x = arrow['start'][0] + (arrow['end'][0] - arrow['start'][0]) * progress
                current_y = arrow['start'][1] + (arrow['end'][1] - arrow['start'][1]) * progress
                self.canvas.coords(
                    arrow['id'],
                    arrow['start'][0], arrow['start'][1],
                    current_x, current_y
                )

            self.canvas.update()
            time.sleep(duration / steps)

    def _animate_value_transfers(self, step, scale, duration):
        """Animate value transfers between nodes"""
        if 'value_transfers' not in step:
            return

        steps = ANIMATION_STEPS
        moving_texts = []
        parent_idx = step['parent']['index']

        for transfer in step['value_transfers']:
            from_node = self.nodes[transfer['from']][0]
            to_node = self.nodes[parent_idx][0]

            from_coords = self.canvas.coords(from_node)
            to_coords = self.canvas.coords(to_node)

            text_data = self._create_moving_text(
                from_coords, to_coords,
                transfer['value'], scale
            )
            moving_texts.append(text_data)

        self._animate_moving_texts(moving_texts, duration)

    def _create_moving_text(self, from_coords, to_coords, value, scale):
        """Create moving text element"""
        start_x = (from_coords[0] + from_coords[2]) / 2
        start_y = (from_coords[1] + from_coords[3]) / 2
        end_x = (to_coords[0] + to_coords[2]) / 2
        end_y = (to_coords[1] + to_coords[3]) / 2

        text_id = self.canvas.create_text(
            start_x, start_y,
            text=str(value),
            fill="red",
            font=(DEFAULT_FONT, round(DEFAULT_FONT_SIZE * scale))
        )

        return {
            'id': text_id,
            'start': (start_x, start_y),
            'end': (end_x, end_y)
        }

    def _animate_moving_texts(self, moving_texts, duration):
        """Animate text movement"""
        steps = ANIMATION_STEPS
        for i in range(steps):
            if not self.animation_running and self.control_panel.get_mode() == "automatic":
                break

            progress = (i + 1) / steps
            for text in moving_texts:
                current_x = text['start'][0] + (text['end'][0] - text['start'][0]) * progress
                current_y = text['start'][1] + (text['end'][1] - text['start'][1]) * progress
                self.canvas.coords(text['id'], current_x, current_y)

            self.canvas.update()
            time.sleep(duration / steps)

        # Clean up moving texts
        for text in moving_texts:
            self.canvas.delete(text['id'])

    def _reverse_parent_children(self, step, duration):
        """Reverse parent-children animation step"""
        parent_idx = step['parent']['index']

        # Animate value transfers back to children
        if 'value_transfers' in step:
            self._reverse_value_transfers(step, duration)

        # Remove arrows
        self._remove_arrows(
            [f"{parent_idx}-{child['index']}" for child in step['children']],
            duration
        )

        # Remove parent node
        if parent_idx in self.nodes:
            self.animate_node_removal(self.nodes[parent_idx], duration)
            for item in self.nodes[parent_idx]:
                self.canvas.delete(item)
            del self.nodes[parent_idx]

    def _reverse_value_transfers(self, step, duration):
        """Reverse value transfer animations"""
        moving_texts = []
        parent_idx = step['parent']['index']

        for transfer in step['value_transfers']:
            from_node = self.nodes[parent_idx][0]
            to_node = self.nodes[transfer['from']][0]

            from_coords = self.canvas.coords(from_node)
            to_coords = self.canvas.coords(to_node)

            text_data = self._create_moving_text(
                from_coords, to_coords,
                transfer['value'],
                self.control_panel.get_scale_value() * self.application.scale_factor
            )
            moving_texts.append(text_data)

        self._animate_moving_texts(moving_texts, duration)

    def _remove_arrows(self, arrow_keys, duration):
        """Remove arrows with animation"""
        arrows_to_remove = []
        for arrow_key in arrow_keys:
            if arrow_key in self.arrows:
                coords = self.canvas.coords(self.arrows[arrow_key])
                arrows_to_remove.append({
                    'id': self.arrows[arrow_key],
                    'start': (coords[0], coords[1]),
                    'end': (coords[2], coords[3])
                })

        steps = ANIMATION_STEPS
        for i in range(steps - 1, -1, -1):
            progress = i / steps
            for arrow in arrows_to_remove:
                current_x = arrow['start'][0] + (arrow['end'][0] - arrow['start'][0]) * progress
                current_y = arrow['start'][1] + (arrow['end'][1] - arrow['start'][1]) * progress
                self.canvas.coords(
                    arrow['id'],
                    arrow['start'][0], arrow['start'][1],
                    current_x, current_y
                )
            self.canvas.update()
            time.sleep(duration / steps)

        # Delete arrows
        for arrow_key in arrow_keys:
            if arrow_key in self.arrows:
                self.canvas.delete(self.arrows[arrow_key])
                del self.arrows[arrow_key]

    def _reverse_root_step(self, step, duration):
        """Reverse root node animation step"""
        # Remove root connections
        arrow_keys = [f"root-{conn['node']}" for conn in step['connections']]
        self._remove_arrows(arrow_keys, duration)

        # Remove root node
        if hasattr(self, 'root_node'):
            self.animate_node_removal(self.root_node, duration)
            for item in self.root_node:
                self.canvas.delete(item)
            delattr(self, 'root_node')