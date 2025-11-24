import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importa ttk per uno stile moderno
import sqlite3

# Creazione della tabella 'users' se non esiste già
def create_users_table():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    # Crea la tabella 'users' se non esiste, aggiungendo la colonna password
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        level TEXT NOT NULL)''')
    # Aggiorna la tabella se manca la colonna password (per retrocompatibilità)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT NOT NULL DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # La colonna esiste già
    conn.commit()
    conn.close()

# Chiama la funzione per creare la tabella users all'inizio del programma
create_users_table()

# Funzione per registrare l'utente
def register_user(combo_level, combo_sport, entry_name, entry_password):
    name = entry_name.get()
    password = entry_password.get()
    level = combo_level.get()
    sport = combo_sport.get()

    if name and password and level and sport:
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
            
            # Inserisci nella tabella utenti anche la password
            cursor.execute("INSERT INTO users (name, password, level) VALUES (?, ?, ?)", (name, password, level))
            
            conn.commit()
            messagebox.showinfo("Registrazione riuscita", f"Utente {name} registrato con successo per {sport}!")
            entry_name.delete(0, tk.END)
            entry_name.insert(0, name)  # Inserire il nome utente nel campo per login
            entry_password.delete(0, tk.END)
        conn.close()
    else:
        messagebox.showwarning("Errore", "Per favore, completa tutti i campi!")

# Funzione di login (accesso)
def login_user(entry_name, entry_password):
    name = entry_name.get()
    password = entry_password.get()

    if name and password:
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()

        if user:
            db_password = user[3]  # id=0, name=1, level=2, password=3
            if password == db_password:
                messagebox.showinfo("Benvenuto", f"Benvenuto, {name}!")
                login_window.destroy()  # Chiudi la finestra di login
                open_main_window(name)  # Apri la finestra principale
            else:
                messagebox.showwarning("Errore", "Password errata.")
        else:
            messagebox.showwarning("Errore", "Il nome utente non esiste. Per favore, registrati.")
        conn.close()
    else:
        messagebox.showwarning("Errore", "Inserisci nome utente e password.")

# Funzione per aprire la finestra principale
def open_main_window(name):
    global combo_sport, entry_event_name, entry_event_date, entry_event_location
    
    # Crea la finestra principale
    root = tk.Tk()
    root.title("Gestione Eventi Sportivi")
    root.geometry("500x500")
    root.configure(bg="#2e2e2e")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Helvetica", 12), padding=10, background="#0d7377", foreground="white")
    style.map("TButton", background=[("active", "#14919b")])
    style.configure("TLabel", font=("Helvetica", 12), padding=10, background="#2e2e2e", foreground="white")
    style.configure("TEntry", font=("Helvetica", 12), padding=10)
    style.configure("TCombobox", font=("Helvetica", 12), padding=10)

    # Titolo benvenuto
    label_welcome = ttk.Label(root, text=f"Benvenuto, {name}!")
    label_welcome.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

    # Sport preferito
    label_sport = ttk.Label(root, text="Sport:")
    label_sport.grid(row=1, column=0, pady=10, padx=10, sticky="e")
    combo_sport = ttk.Combobox(root, state="readonly")
    combo_sport.set("BeachVolley")
    combo_sport['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport.grid(row=1, column=1, pady=10, padx=10)

    # Visualizza Utenti e Eventi
    btn_show_users = ttk.Button(root, text="Visualizza Utenti", command=show_users)
    btn_show_users.grid(row=2, column=0, columnspan=2, pady=10)

    btn_show_events = ttk.Button(root, text="Visualizza Eventi", command=show_events)
    btn_show_events.grid(row=3, column=0, columnspan=2, pady=10)

    # Creazione Evento
    label_event_name = ttk.Label(root, text="Nome Evento:")
    label_event_name.grid(row=4, column=0, pady=10, padx=10, sticky="e")
    entry_event_name = ttk.Entry(root, style="TEntry")
    entry_event_name.grid(row=4, column=1, pady=10, padx=10)

    label_event_date = ttk.Label(root, text="Data Evento:")
    label_event_date.grid(row=5, column=0, pady=10, padx=10, sticky="e")
    entry_event_date = ttk.Entry(root, style="TEntry")
    entry_event_date.grid(row=5, column=1, pady=10, padx=10)

    label_event_location = ttk.Label(root, text="Luogo Evento:")
    label_event_location.grid(row=6, column=0, pady=10, padx=10, sticky="e")
    entry_event_location = ttk.Entry(root, style="TEntry")
    entry_event_location.grid(row=6, column=1, pady=10, padx=10)

    btn_create_event = ttk.Button(root, text="Crea Evento", command=create_event)
    btn_create_event.grid(row=7, column=0, columnspan=2, pady=10)

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

# Funzione per mostrare gli eventi per lo sport selezionato
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
login_window.geometry("1280x720")
login_window.configure(bg="#2e2e2e")

# Stile per i bottoni della finestra di login
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Helvetica", 12), padding=10, background="#0d7377", foreground="white")
style.map("TButton", background=[("active", "#14919b")])

# Layout per il login
label_name = tk.Label(login_window, text="Nome utente:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
label_name.pack(pady=10)

entry_name = tk.Entry(login_window, font=("Helvetica", 12))
entry_name.pack(pady=10)

# Campo password
label_password = tk.Label(login_window, text="Password:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
label_password.pack(pady=5)
entry_password = tk.Entry(login_window, show="*", font=("Helvetica", 12))
entry_password.pack(pady=5)

btn_login = tk.Button(login_window, text="Accedi", command=lambda: login_user(entry_name, entry_password), 
                      bg="#0d7377", fg="white", font=("Helvetica", 12), activebackground="#14919b", activeforeground="white", padx=20, pady=10)
btn_login.pack(pady=20)


# Livello di gioco
label_level = tk.Label(login_window, text="Livello di gioco:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
label_level.pack(pady=5)
combo_level = ttk.Combobox(login_window, state="readonly", font=("Helvetica", 12))
combo_level['values'] = ("Principiante", "Intermedio", "Avanzato")
combo_level.set("Principiante")
combo_level.pack(pady=5)

# Sport preferito
label_sport = tk.Label(login_window, text="Sport preferito:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
label_sport.pack(pady=5)
combo_sport = ttk.Combobox(login_window, state="readonly", font=("Helvetica", 12))
combo_sport['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
combo_sport.set("BeachVolley")
combo_sport.pack(pady=5)

btn_register = tk.Button(login_window, text="Registrati", command=lambda: register_user(combo_level, combo_sport, entry_name, entry_password),
                         bg="#0d7377", fg="white", font=("Helvetica", 12), activebackground="#14919b", activeforeground="white", padx=20, pady=10)
btn_register.pack(pady=10)

login_window.mainloop()
