import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importa ttk per uno stile moderno
import sqlite3

# Funzione per registrare l'utente
def register_user():
    name = entry_name.get()
    level = combo_level.get()
    sport = combo_sport.get()

    if name and level and sport:
        # Verifica se il nome utente esiste già
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            messagebox.showwarning("Errore", "Il nome utente è già in uso.")
        else:
            # Inserire i dati nella tabella corrispondente allo sport scelto
            if sport == "BeachVolley":
                cursor.execute("INSERT INTO beachvolley (name, level) VALUES (?, ?)", (name, level))
            elif sport == "Tennis":
                cursor.execute("INSERT INTO tennis (name, level) VALUES (?, ?)", (name, level))
            elif sport == "Calcetto":
                cursor.execute("INSERT INTO calcetto (name, level) VALUES (?, ?)", (name, level))
            elif sport == "Padel":
                cursor.execute("INSERT INTO padel (name, level) VALUES (?, ?)", (name, level))
            
            # Creare la tabella utenti se non esiste
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, level TEXT)")
            cursor.execute("INSERT INTO users (name, level) VALUES (?, ?)", (name, level))
            
            conn.commit()
            messagebox.showinfo("Registrazione riuscita", f"Utente {name} registrato con successo per {sport}!")
            entry_name.delete(0, tk.END)
            entry_name.insert(0, name)  # Inserire il nome utente nel campo per login
        conn.close()
    else:
        messagebox.showwarning("Errore", "Per favore, completa tutti i campi!")

# Funzione di login (accesso)
def login_user():
    name = entry_name.get()

    if name:
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Benvenuto", f"Benvenuto, {name}!")
            login_window.destroy()  # Chiudi la finestra di login
            open_main_window(name)  # Apri la finestra principale
        else:
            messagebox.showwarning("Errore", "Il nome utente non esiste. Per favore, registrati.")
        conn.close()
    else:
        messagebox.showwarning("Errore", "Inserisci il nome utente.")

# Funzione per aprire la finestra principale
def open_main_window(name):
    # Crea la finestra principale
    root = tk.Tk()
    root.title("Gestione Eventi Sportivi")
    root.geometry("500x500")

    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10, background="#444444", foreground="white")
    style.configure("TLabel", font=("Helvetica", 12), padding=10, background="#2e2e2e", foreground="white")
    style.configure("TEntry", font=("Helvetica", 12), padding=10)
    style.configure("TOptionMenu", font=("Helvetica", 12), padding=10)

    # Layout per la registrazione dell'utente (usando grid per una disposizione più spaziosa)
    label_name = ttk.Label(root, text="Nome:")
    label_name.grid(row=0, column=0, pady=10, padx=10, sticky="e")
    entry_name = ttk.Entry(root, style="TEntry")
    entry_name.grid(row=0, column=1, pady=10, padx=10)

    label_level = ttk.Label(root, text="Livello di gioco:")
    label_level.grid(row=1, column=0, pady=10, padx=10, sticky="e")
    combo_level = ttk.Combobox(root, state="readonly", style="TEntry")
    combo_level.set("Principiante")
    combo_level['values'] = ("Principiante", "Intermedio", "Avanzato")
    combo_level.grid(row=1, column=1, pady=10, padx=10)

    label_sport = ttk.Label(root, text="Sport preferito:")
    label_sport.grid(row=2, column=0, pady=10, padx=10, sticky="e")
    combo_sport = ttk.Combobox(root, state="readonly", style="TEntry")
    combo_sport.set("BeachVolley")
    combo_sport['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport.grid(row=2, column=1, pady=10, padx=10)

    btn_register = ttk.Button(root, text="Registrati", command=register_user)
    btn_register.grid(row=3, column=0, columnspan=2, pady=20)

    # Pulsante per visualizzare utenti ed eventi
    btn_show_users = ttk.Button(root, text="Visualizza Utenti", command=show_users)
    btn_show_users.grid(row=4, column=0, columnspan=2, pady=10)

    btn_create_event = ttk.Button(root, text="Crea Evento", command=create_event)
    btn_create_event.grid(row=5, column=0, columnspan=2, pady=10)

    btn_show_events = ttk.Button(root, text="Visualizza Eventi", command=show_events)
    btn_show_events.grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()

# Funzione per mostrare gli utenti registrati per lo sport selezionato
def show_users():
    sport = combo_sport.get()

    # Connettersi al database
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    # Esegui la query per ottenere gli utenti per lo sport selezionato
    cursor.execute(f"SELECT * FROM {sport.lower()}")
    users = cursor.fetchall()

    # Mostra i risultati in una finestra di dialogo
    user_list = "\n".join([f"{user[1]} (Livello: {user[2]})" for user in users])

    if user_list:
        messagebox.showinfo(f"Utenti per {sport}", user_list)
    else:
        messagebox.showinfo(f"Utenti per {sport}", "Nessun utente trovato per questo sport.")
    
    conn.close()

# Funzione per creare un evento
def create_event():
    event_name = entry_event_name.get()
    event_date = entry_event_date.get()
    event_location = entry_event_location.get()
    sport = combo_sport.get()

    if event_name and event_date and event_location:
        # Connettersi al database
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()

        # Creare la tabella eventi per ogni sport
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {sport.lower()}_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_location TEXT NOT NULL
        )
        ''')

        # Inserire i dati dell'evento nella tabella
        cursor.execute(f"INSERT INTO {sport.lower()}_events (event_name, event_date, event_location) VALUES (?, ?, ?)", 
                       (event_name, event_date, event_location))

        conn.commit()
        conn.close()

        messagebox.showinfo("Evento creato", f"L'evento '{event_name}' è stato creato con successo!")
        entry_event_name.delete(0, tk.END)
        entry_event_date.delete(0, tk.END)
        entry_event_location.delete(0, tk.END)
    else:
        messagebox.showwarning("Errore", "Per favore, completa tutti i campi!")

# Funzione per mostrare gli eventi
def show_events():
    sport = combo_sport.get()

    # Connettersi al database
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    # Esegui la query per ottenere gli eventi per lo sport selezionato
    cursor.execute(f"SELECT * FROM {sport.lower()}_events")
    events = cursor.fetchall()

    # Mostra i risultati in una finestra di dialogo
    event_list = "\n".join([f"Evento: {event[1]}, Data: {event[2]}, Location: {event[3]}" for event in events])

    if event_list:
        messagebox.showinfo(f"Eventi per {sport}", event_list)
    else:
        messagebox.showinfo(f"Eventi per {sport}", "Nessun evento trovato per questo sport.")
    
    conn.close()

# Finestra di login
login_window = tk.Tk()
login_window.title("Login / Registrazione")
login_window.geometry("400x300")

# Layout per il login
label_name = tk.Label(login_window, text="Nome utente:")
label_name.pack(pady=10)

entry_name = tk.Entry(login_window)
entry_name.pack(pady=10)

btn_login = tk.Button(login_window, text="Accedi", command=login_user)
btn_login.pack(pady=20)

btn_register = tk.Button(login_window, text="Registrati", command=register_user)
btn_register.pack(pady=10)

login_window.mainloop()
