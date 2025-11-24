import tkinter as tk
from tkinter import messagebox
import sqlite3

# Funzione per registrare l'utente
def register_user():
    name = entry_name.get()
    level = combo_level.get()
    sport = combo_sport.get()

    if name and level and sport:
        # Connettersi al database
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()

        # Inserire i dati nella tabella corrispondente allo sport scelto
        if sport == "BeachVolley":
            cursor.execute("INSERT INTO beachvolley (name, level) VALUES (?, ?)", (name, level))
        elif sport == "Tennis":
            cursor.execute("INSERT INTO tennis (name, level) VALUES (?, ?)", (name, level))
        elif sport == "Calcetto":
            cursor.execute("INSERT INTO calcetto (name, level) VALUES (?, ?)", (name, level))
        elif sport == "Padel":
            cursor.execute("INSERT INTO padel (name, level) VALUES (?, ?)", (name, level))

        # Commit dei cambiamenti e chiusura della connessione
        conn.commit()
        conn.close()

        messagebox.showinfo("Registrazione riuscita", f"Utente {name} registrato con successo per {sport}!")
        entry_name.delete(0, tk.END)
    else:
        messagebox.showwarning("Errore", "Per favore, completa tutti i campi!")

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
        cursor.execute(f"INSERT INTO {sport.lower()}_events (event_name, event_date, event_location) VALUES (?, ?, ?)", (event_name, event_date, event_location))

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

# Creazione della finestra principale
root = tk.Tk()
root.title("Registrazione Utente")

# Layout per la registrazione dell'utente
label_name = tk.Label(root, text="Nome:")
label_name.pack()
entry_name = tk.Entry(root)
entry_name.pack()

label_level = tk.Label(root, text="Livello di gioco:")
label_level.pack()
combo_level = tk.StringVar(root)
combo_level.set("Principiante")
level_menu = tk.OptionMenu(root, combo_level, "Principiante", "Intermedio", "Avanzato")
level_menu.pack()

label_sport = tk.Label(root, text="Sport preferito:")
label_sport.pack()
combo_sport = tk.StringVar(root)
combo_sport.set("BeachVolley")  # Sport predefinito
sport_menu = tk.OptionMenu(root, combo_sport, "BeachVolley", "Tennis", "Calcetto", "Padel")
sport_menu.pack()

btn_register = tk.Button(root, text="Registrati", command=register_user)
btn_register.pack()

# Layout per la creazione dell'evento
label_event_name = tk.Label(root, text="Nome Evento:")
label_event_name.pack()
entry_event_name = tk.Entry(root)
entry_event_name.pack()

label_event_date = tk.Label(root, text="Data Evento:")
label_event_date.pack()
entry_event_date = tk.Entry(root)
entry_event_date.pack()

label_event_location = tk.Label(root, text="Location Evento:")
label_event_location.pack()
entry_event_location = tk.Entry(root)
entry_event_location.pack()

btn_create_event = tk.Button(root, text="Crea Evento", command=create_event)
btn_create_event.pack()

# Pulsanti per visualizzare utenti ed eventi
btn_show_users = tk.Button(root, text="Visualizza Utenti", command=show_users)
btn_show_users.pack()

btn_show_events = tk.Button(root, text="Visualizza Eventi", command=show_events)
btn_show_events.pack()

# Avvio dell'applicazione Tkinter
root.mainloop()
