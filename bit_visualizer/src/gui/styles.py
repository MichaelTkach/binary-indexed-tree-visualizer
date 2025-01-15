from tkinter import ttk

def setup_styles():
    """Configure custom styles for the application"""
    style = ttk.Style()

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

    style.configure(
        'Menu.TButton',
        padding=(30, 15),
        font=('Arial', 14, 'bold'),
        width=100,
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

    style.configure(
        'Control.TButton',
        padding=(15, 8),
        font=('Arial', 11),
        borderwidth=2,
        width=10,
        relief="raised",
        background="#31b834",
        foreground="white"
    )
    style.map('Control.TButton',
              background=[('pressed', '#b9e4c1'), ('active', '#6dca61'), ('disabled', '#dbd3e6')],
              relief=[('pressed', 'sunken')],
              foreground=[('pressed', 'white'), ('active', 'yellow'), ('disabled', 'black')]
              )

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

    style.configure(
        'Custom.TRadiobutton',
        font=('Arial', 11, 'bold'),
        padding=5
    )

    style.configure(
        'Custom.TEntry',
        padding=5,
        font=('Arial', 11),
    )

    style.configure(
        'Custom.Horizontal.TScale',
        sliderthickness=20,
        sliderrelief="raised"
    )

    style.configure(
        'Title.TLabel',
        font=('Arial', 24, 'bold')
    )

    return style