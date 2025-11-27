# Componenti GUI standardizzati
import tkinter as tk
from tkinter import ttk
from gui_theme import THEME, FONTS, PADDING, DIMENSIONS

def create_window(title, width=DIMENSIONS["window_width"], height=DIMENSIONS["window_height"]):
    """Crea una finestra con tema consistente"""
    window = tk.Toplevel()
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.configure(bg=THEME["bg_primary"])
    return window

def create_title_label(parent, text, bg=THEME["bg_primary"]):
    """Crea un label titolo"""
    label = tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=THEME["fg_primary"],
        font=FONTS["title"]
    )
    return label

def create_subtitle_label(parent, text, bg=THEME["bg_primary"]):
    """Crea un label sottotitolo"""
    label = tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=THEME["fg_primary"],
        font=FONTS["subtitle"]
    )
    return label

def create_label(parent, text, bg=THEME["bg_primary"], font_type="label"):
    """Crea un label standard"""
    label = tk.Label(
        parent,
        text=text,
        bg=bg,
        fg=THEME["fg_primary"],
        font=FONTS[font_type]
    )
    return label

def create_text_widget(parent, height=DIMENSIONS["text_height"], width=DIMENSIONS["text_width"], 
                      text_color=THEME["fg_primary"]):
    """Crea un widget Text con tema"""
    text = tk.Text(
        parent,
        height=height,
        width=width,
        bg=THEME["bg_secondary"],
        fg=text_color,
        font=FONTS["text"]
    )
    return text

def create_combobox(parent, width=30, font_type="label"):
    """Crea una Combobox con tema"""
    combo = ttk.Combobox(
        parent,
        state="readonly",
        font=FONTS[font_type],
        width=width
    )
    return combo

def create_primary_button(parent, text, command=None, padx=PADDING["large"], pady=PADDING["medium"]):
    """Crea un bottone primario"""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=THEME["btn_primary_bg"],
        fg=THEME["btn_primary_fg"],
        font=FONTS["label"],
        activebackground=THEME["btn_primary_active_bg"],
        activeforeground=THEME["btn_primary_active_fg"],
        padx=padx,
        pady=pady
    )
    return btn

def create_secondary_button(parent, text, command=None, padx=PADDING["large"], pady=PADDING["medium"]):
    """Crea un bottone secondario"""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=THEME["btn_secondary_bg"],
        fg=THEME["btn_secondary_fg"],
        font=FONTS["label"],
        activebackground=THEME["btn_secondary_active_bg"],
        activeforeground=THEME["btn_secondary_active_fg"],
        padx=padx,
        pady=pady
    )
    return btn

def create_small_button(parent, text, command=None):
    """Crea un bottone piccolo"""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=THEME["btn_primary_bg"],
        fg=THEME["btn_primary_fg"],
        font=FONTS["smaller"],
        activebackground=THEME["btn_primary_active_bg"],
        activeforeground=THEME["btn_primary_active_fg"]
    )
    return btn

def create_frame(parent, bg=THEME["bg_primary"]):
    """Crea un frame con tema"""
    frame = tk.Frame(parent, bg=bg)
    return frame

def set_text_message(text_widget, message, color=THEME["fg_success"]):
    """Aggiorna un widget Text con un messaggio e colore"""
    text_widget.config(fg=color)
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, message)

def update_text_content(text_widget, content, readonly=True):
    """Aggiorna il contenuto di un widget Text"""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, content)
    if readonly:
        text_widget.config(state=tk.DISABLED)
