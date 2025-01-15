import json
from tkinter import filedialog, messagebox
from ..utils.constants import JSON_FILETYPES


def save_state(initial_array, bit_array, current_step):
    """Save complete diagram state to a file"""
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=JSON_FILETYPES
        )
        if not filename:
            return None

        state = {
            'initial_array': initial_array,
            'bit_array': bit_array,
            'current_step': current_step
        }

        with open(filename, 'w') as f:
            json.dump(state, f)

        return True

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        return False


def load_state():
    """Load state from a file"""
    try:
        filename = filedialog.askopenfilename(
            filetypes=JSON_FILETYPES
        )

        if not filename:
            return None

        with open(filename, 'r') as f:
            state = json.load(f)

        return state

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {str(e)}")
        return None