import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importa ttk per uno stile più moderno
import sqlite3

# Creazione della tabella 'users' se non esiste già
def create_users_table():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    # Crea la tabella 'users' se non esiste
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

# Dizionario con i limiti di partecipanti per sport
SPORT_LIMITS = {
    "BeachVolley": 8,
    "Tennis": 2,
    "Calcetto": 10,
    "Padel": 4
}

# Variabili globali per le finestre persistenti
users_window_instance = None
events_window_instance = None
create_event_window_instance = None

# Funzione per creare tabella partecipanti per un evento
def create_event_participants_table(sport, event_id):
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    try:
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {sport.lower()}_event_{event_id}_participants (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE)''')
        conn.commit()
    except Exception as e:
        print(f"Errore creazione tabella: {e}")
    conn.close()

# Funzione per iscrivere un utente a un evento
def register_to_event(sport, event_id, username):
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    try:
        # Crea la tabella dei partecipanti se non esiste
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {sport.lower()}_event_{event_id}_participants (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE)''')
        conn.commit()
        
        # Verifica il numero di partecipanti
        cursor.execute(f"SELECT COUNT(*) FROM {sport.lower()}_event_{event_id}_participants")
        current_participants = cursor.fetchone()[0]
        max_participants = SPORT_LIMITS.get(sport, 0)
        
        if current_participants >= max_participants:
            return False, f"✗ L'evento è pieno! Massimo {max_participants} partecipanti."
        
        # Verifica se l'utente è già iscritto
        cursor.execute(f"SELECT * FROM {sport.lower()}_event_{event_id}_participants WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "✗ Sei già iscritto a questo evento!"
        
        # Iscrivere l'utente
        cursor.execute(f"INSERT INTO {sport.lower()}_event_{event_id}_participants (username) VALUES (?)", (username,))
        conn.commit()
        return True, f"✓ Iscritto con successo! Partecipanti: {current_participants + 1}/{max_participants}"
    except Exception as e:
        return False, f"✗ Errore: {str(e)}"
    finally:
        conn.close()

# Funzione per ottenere il numero di partecipanti
def get_event_participants_count(event_id):
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    try:
        # Prima recupera lo sport dall'evento
        cursor.execute("SELECT sport FROM sport_events WHERE id = ?", (event_id,))
        result = cursor.fetchone()
        if result:
            sport = result[0]
            cursor.execute(f"SELECT COUNT(*) FROM {sport.lower()}_event_{event_id}_participants")
            count = cursor.fetchone()[0]
        else:
            count = 0
    except Exception as e:
        print(f"Errore get_event_participants_count: {e}")
        count = 0
    conn.close()
    return count

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

# Variabili globali per le finestre
users_window_instance = None
events_window_instance = None
create_event_window_instance = None

# Funzione per aprire la finestra principale
def open_show_users_window():
    global users_window_instance
    
    # Se la finestra è già aperta, portala in primo piano
    if users_window_instance and users_window_instance.winfo_exists():
        users_window_instance.lift()
        users_window_instance.focus()
        return
    
    users_window = tk.Toplevel()
    users_window_instance = users_window
    users_window.title("Visualizza Utenti")
    users_window.geometry("600x500")
    users_window.configure(bg="#2e2e2e")
    
    # Titolo
    label_title = tk.Label(users_window, text="Visualizza Utenti", bg="#2e2e2e", fg="white", font=("Helvetica", 14, "bold"))
    label_title.pack(pady=20)
    
    # Sport preferito
    label_sport = tk.Label(users_window, text="Seleziona Sport:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_sport.pack(pady=10)
    combo_sport_users = ttk.Combobox(users_window, state="readonly", font=("Helvetica", 12), width=30)
    combo_sport_users['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport_users.set("BeachVolley")
    combo_sport_users.pack(pady=10)
    
    # Area per i risultati
    text_results = tk.Text(users_window, height=12, width=60, bg="#1e1e1e", fg="white", font=("Helvetica", 11))
    text_results.pack(pady=10, padx=10)
    
    # Area messaggi
    text_messages = tk.Text(users_window, height=3, width=60, bg="#1e1e1e", fg="#00ff00", font=("Helvetica", 10))
    text_messages.pack(pady=5, padx=10)
    
    # Funzione per visualizzare gli utenti
    def show_users_from_window():
        sport = combo_sport_users.get()
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {sport.lower()}")
            users = cursor.fetchall()
            
            text_results.delete(1.0, tk.END)
            if users:
                for user in users:
                    text_results.insert(tk.END, f"{user[1]} (Livello: {user[2]})\n")
                text_messages.config(fg="#00ff00")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, f"✓ Utenti caricati: {len(users)}")
            else:
                text_results.insert(tk.END, f"Nessun utente trovato per {sport}.")
                text_messages.config(fg="#ffaa00")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, "Nessun utente per questo sport")
        except Exception as e:
            text_results.delete(1.0, tk.END)
            text_messages.config(fg="#ff0000")
            text_messages.delete(1.0, tk.END)
            text_messages.insert(tk.END, f"Errore: {str(e)}")
        conn.close()
    
    # Bottone visualizza
    btn_visualize = tk.Button(users_window, text="Visualizza", 
                              command=show_users_from_window,
                              bg="#0d7377", fg="white", font=("Helvetica", 12), 
                              activebackground="#14919b", activeforeground="white", padx=20, pady=10)
    btn_visualize.pack(pady=20)
    btn_visualize.pack(pady=20)
    
    # Carica gli utenti al primo sport
    show_users_from_window()

def open_show_events_window(username):
    global events_window_instance
    
    # Se la finestra è già aperta, portala in primo piano e aggiorna
    if events_window_instance and events_window_instance.winfo_exists():
        events_window_instance.lift()
        events_window_instance.focus()
        return
    
    events_window = tk.Toplevel()
    events_window_instance = events_window
    events_window.title("Visualizza Eventi")
    events_window.geometry("650x550")
    events_window.configure(bg="#2e2e2e")
    
    # Titolo
    label_title = tk.Label(events_window, text="Visualizza Eventi", bg="#2e2e2e", fg="white", font=("Helvetica", 14, "bold"))
    label_title.pack(pady=20)
    
    # Sport preferito
    label_sport = tk.Label(events_window, text="Seleziona Sport:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_sport.pack(pady=10)
    combo_sport_events = ttk.Combobox(events_window, state="readonly", font=("Helvetica", 12), width=30)
    combo_sport_events['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport_events.set("BeachVolley")
    combo_sport_events.pack(pady=10)
    
    # Area per i risultati
    text_results = tk.Text(events_window, height=10, width=70, bg="#1e1e1e", fg="white", font=("Helvetica", 11))
    text_results.pack(pady=10, padx=10)
    
    # Selezione evento
    label_select_event = tk.Label(events_window, text="Seleziona Evento:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_select_event.pack(pady=10)
    combo_events = ttk.Combobox(events_window, state="readonly", font=("Helvetica", 12), width=70)
    combo_events.pack(pady=10, padx=10)
    
    # Area messaggi
    text_messages = tk.Text(events_window, height=3, width=70, bg="#1e1e1e", fg="#00ff00", font=("Helvetica", 10))
    text_messages.pack(pady=5, padx=10)
    
    # Lista per tenere traccia degli event ID
    events_list = []
    
    # Funzione per visualizzare gli eventi
    def show_events_from_window():
        nonlocal events_list
        sport = combo_sport_events.get()
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM sport_events WHERE sport = '{sport}'")
            events = cursor.fetchall()
            
            text_results.delete(1.0, tk.END)
            events_list = []
            combo_events['values'] = []
            
            if events:
                event_list = []
                for i, event in enumerate(events, start=1):  # Inizia da 1
                    event_id = event[0]
                    event_name = event[2]
                    event_date = event[3]
                    participants = get_event_participants_count(event_id)
                    max_participants = SPORT_LIMITS.get(sport, 0)
                    
                    text_results.insert(tk.END, f"[{i}] {event_name} - {event_date} ({participants}/{max_participants} partecipanti)\n")
                    events_list.append((event_id, sport))
                    event_list.append(f"{i}. {event_name}")
                
                combo_events['values'] = event_list
                text_messages.config(fg="#00ff00")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, f"✓ {len(events)} eventi trovati")
            else:
                text_results.insert(tk.END, f"Nessun evento trovato per {sport}.")
                text_messages.config(fg="#ffaa00")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, "Nessun evento disponibile")
        except Exception as e:
            text_results.delete(1.0, tk.END)
            text_results.insert(tk.END, f"Errore: {str(e)}")
            text_messages.config(fg="#ff0000")
            text_messages.delete(1.0, tk.END)
            text_messages.insert(tk.END, f"Errore: {str(e)}")
        conn.close()
    
    # Funzione per iscriversi all'evento
    def subscribe_to_event():
        try:
            if not combo_events.get():
                text_messages.config(fg="#ff0000")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, "✗ Seleziona un evento")
                return
            
            event_num = int(combo_events.get().split(".")[0])
            if event_num < 1 or event_num > len(events_list):
                text_messages.config(fg="#ff0000")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, "✗ Numero evento non valido!")
                return
            
            event_id, sport = events_list[event_num - 1]
            success, message = register_to_event(sport, event_id, username)
            
            if success:
                text_messages.config(fg="#00ff00")
                show_events_from_window()  # Ricarica gli eventi
                combo_events.set('')
            else:
                text_messages.config(fg="#ff0000")
            
            text_messages.delete(1.0, tk.END)
            text_messages.insert(tk.END, message)
        except (ValueError, IndexError) as e:
            text_messages.config(fg="#ff0000")
            text_messages.delete(1.0, tk.END)
            text_messages.insert(tk.END, f"✗ Errore: {str(e)}")
    
    # Bottoni
    button_frame = tk.Frame(events_window, bg="#2e2e2e")
    button_frame.pack(pady=20)
    
    btn_visualize = tk.Button(button_frame, text="Visualizza", 
                              command=show_events_from_window,
                              bg="#0d7377", fg="white", font=("Helvetica", 12), 
                              activebackground="#14919b", activeforeground="white", padx=20, pady=10)
    btn_visualize.pack(side=tk.LEFT, padx=10)
    
    btn_subscribe = tk.Button(button_frame, text="Iscriviti", command=subscribe_to_event,
                             bg="#14919b", fg="white", font=("Helvetica", 12), 
                             activebackground="#0d7377", activeforeground="white", padx=20, pady=10)
    btn_subscribe.pack(side=tk.LEFT, padx=10)
    
    # Carica gli eventi al primo sport
    show_events_from_window()

def open_create_event_window(sport_selected):
    global create_event_window_instance
    
    # Se la finestra è già aperta, portala in primo piano
    if create_event_window_instance and create_event_window_instance.winfo_exists():
        create_event_window_instance.lift()
        create_event_window_instance.focus()
        return
    
    create_window = tk.Toplevel()
    create_event_window_instance = create_window
    create_window.title("Crea Evento")
    create_window.geometry("500x450")
    create_window.configure(bg="#2e2e2e")
    
    # Titolo
    label_title = tk.Label(create_window, text="Crea Nuovo Evento", bg="#2e2e2e", fg="white", font=("Helvetica", 14, "bold"))
    label_title.pack(pady=20)
    
    # Sport
    label_sport = tk.Label(create_window, text="Sport:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_sport.pack(pady=10)
    combo_sport_create = ttk.Combobox(create_window, state="readonly", font=("Helvetica", 12), width=30)
    combo_sport_create['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport_create.set(sport_selected)
    combo_sport_create.pack(pady=10)
    
    # Nome evento
    label_event_name = tk.Label(create_window, text="Nome Evento:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_event_name.pack(pady=5)
    entry_event_name = tk.Entry(create_window, font=("Helvetica", 12), width=30)
    entry_event_name.pack(pady=5)
    
    # Data evento
    label_event_date = tk.Label(create_window, text="Data Evento:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_event_date.pack(pady=5)
    entry_event_date = tk.Entry(create_window, font=("Helvetica", 12), width=30)
    entry_event_date.pack(pady=5)
    
    # Luogo evento
    label_event_location = tk.Label(create_window, text="Luogo Evento:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_event_location.pack(pady=5)
    entry_event_location = tk.Entry(create_window, font=("Helvetica", 12), width=30)
    entry_event_location.pack(pady=5)
    
    # Area messaggi
    text_messages = tk.Text(create_window, height=3, width=50, bg="#1e1e1e", fg="#00ff00", font=("Helvetica", 10))
    text_messages.pack(pady=10, padx=10)
    
    # Bottone crea
    def create_event_from_window():
        event_name = entry_event_name.get()
        event_date = entry_event_date.get()
        event_location = entry_event_location.get()
        sport = combo_sport_create.get()
        
        if event_name and event_date and event_location:
            try:
                conn = sqlite3.connect('sports.db')
                cursor = conn.cursor()
                
                # Crea nella tabella centrale sport_events
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS sport_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    event_location TEXT NOT NULL
                )
                ''')
                
                cursor.execute("INSERT INTO sport_events (sport, event_name, event_date, event_location) VALUES (?, ?, ?, ?)", 
                               (sport, event_name, event_date, event_location))
                
                conn.commit()
                
                # Ottieni l'ID dell'evento appena creato
                cursor.execute("SELECT last_insert_rowid()")
                event_id = cursor.fetchone()[0]
                
                conn.close()
                
                # Crea la tabella dei partecipanti per questo evento
                create_event_participants_table(sport, event_id)
                
                text_messages.config(fg="#00ff00")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, f"✓ Evento '{event_name}' creato con successo!")
                entry_event_name.delete(0, tk.END)
                entry_event_date.delete(0, tk.END)
                entry_event_location.delete(0, tk.END)
            except Exception as e:
                text_messages.config(fg="#ff0000")
                text_messages.delete(1.0, tk.END)
                text_messages.insert(tk.END, f"✗ Errore: {str(e)}")
        else:
            text_messages.config(fg="#ff0000")
            text_messages.delete(1.0, tk.END)
            text_messages.insert(tk.END, "✗ Compila tutti i campi!")
    
    btn_create = tk.Button(create_window, text="Crea Evento", command=create_event_from_window,
                          bg="#0d7377", fg="white", font=("Helvetica", 12), 
                          activebackground="#14919b", activeforeground="white", padx=20, pady=10)
    btn_create.pack(pady=20)

def open_main_window(name):
    global combo_sport
    
    # Crea la finestra principale
    root = tk.Tk()
    root.title("Gestione Eventi Sportivi")
    root.geometry("600x500")
    root.configure(bg="#2e2e2e")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Helvetica", 12), padding=10, background="#0d7377", foreground="white")
    style.map("TButton", background=[("active", "#14919b")])
    style.configure("TLabel", font=("Helvetica", 12), padding=10, background="#2e2e2e", foreground="white")
    style.configure("TEntry", font=("Helvetica", 12), padding=10)
    style.configure("TCombobox", font=("Helvetica", 12), padding=10)

    # Titolo benvenuto
    label_welcome = ttk.Label(root, text=f"Benvenuto, {name}!", font=("Helvetica", 16, "bold"))
    label_welcome.pack(pady=30)

    # Sport preferito per le azioni
    label_sport = ttk.Label(root, text="Seleziona lo sport:")
    label_sport.pack(pady=10)
    combo_sport = ttk.Combobox(root, state="readonly", font=("Helvetica", 12), width=30)
    combo_sport.set("BeachVolley")
    combo_sport['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport.pack(pady=10)

    # Separator
    label_separator = ttk.Label(root, text="Cosa vuoi fare?", font=("Helvetica", 12, "bold"))
    label_separator.pack(pady=20)

    # Pulsanti principali
    btn_show_users = tk.Button(root, text="Visualizza Utenti", command=open_show_users_window,
                              bg="#0d7377", fg="white", font=("Helvetica", 12), 
                              activebackground="#14919b", activeforeground="white", padx=30, pady=15, width=25)
    btn_show_users.pack(pady=10)

    btn_show_events = tk.Button(root, text="Visualizza Eventi", command=lambda: open_show_events_window(name),
                               bg="#0d7377", fg="white", font=("Helvetica", 12), 
                               activebackground="#14919b", activeforeground="white", padx=30, pady=15, width=25)
    btn_show_events.pack(pady=10)

    btn_create_event = tk.Button(root, text="Crea Evento", command=lambda: open_create_event_window(combo_sport.get()),
                                bg="#0d7377", fg="white", font=("Helvetica", 12), 
                                activebackground="#14919b", activeforeground="white", padx=30, pady=15, width=25)
    btn_create_event.pack(pady=10)

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

# Finestra di registrazione separata
def open_registration_window():
    reg_window = tk.Toplevel(login_window)
    reg_window.title("Registrazione")
    reg_window.geometry("400x400")
    reg_window.configure(bg="#2e2e2e")
    
    # Titolo registrazione
    label_title = tk.Label(reg_window, text="Registrazione Nuovo Utente", bg="#2e2e2e", fg="white", font=("Helvetica", 14, "bold"))
    label_title.pack(pady=20)
    
    # Nome utente
    label_reg_name = tk.Label(reg_window, text="Nome utente:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_reg_name.pack(pady=5)
    entry_reg_name = tk.Entry(reg_window, font=("Helvetica", 12))
    entry_reg_name.pack(pady=5)
    
    # Password
    label_reg_password = tk.Label(reg_window, text="Password:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_reg_password.pack(pady=5)
    entry_reg_password = tk.Entry(reg_window, show="*", font=("Helvetica", 12))
    entry_reg_password.pack(pady=5)
    
    # Livello di gioco
    label_reg_level = tk.Label(reg_window, text="Livello di gioco:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_reg_level.pack(pady=5)
    combo_reg_level = ttk.Combobox(reg_window, state="readonly", font=("Helvetica", 12))
    combo_reg_level['values'] = ("Principiante", "Intermedio", "Avanzato")
    combo_reg_level.set("Principiante")
    combo_reg_level.pack(pady=5)
    
    # Sport preferito
    label_reg_sport = tk.Label(reg_window, text="Sport preferito:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_reg_sport.pack(pady=5)
    combo_reg_sport = ttk.Combobox(reg_window, state="readonly", font=("Helvetica", 12))
    combo_reg_sport['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_reg_sport.set("BeachVolley")
    combo_reg_sport.pack(pady=5)
    
    # Bottone registrati
    btn_reg_submit = tk.Button(reg_window, text="Registrati", 
                               command=lambda: register_user(combo_reg_level, combo_reg_sport, entry_reg_name, entry_reg_password),
                               bg="#0d7377", fg="white", font=("Helvetica", 12), activebackground="#14919b", activeforeground="white", padx=20, pady=10)
    btn_reg_submit.pack(pady=20)

# Finestra di login
login_window = tk.Tk()
login_window.title("Login / Registrazione")
login_window.geometry("800x600")
login_window.configure(bg="#2e2e2e")

# Stile per i bottoni della finestra di login
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Helvetica", 12), padding=10, background="#0d7377", foreground="white")
style.map("TButton", background=[("active", "#14919b")])

# Titolo login
label_title = tk.Label(login_window, text="Accedi", bg="#2e2e2e", fg="white", font=("Helvetica", 14, "bold"))
label_title.pack(pady=20)

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

# Bottone Accedi
btn_login = tk.Button(login_window, text="Accedi", command=lambda: login_user(entry_name, entry_password), 
                      bg="#0d7377", fg="white", font=("Helvetica", 12), activebackground="#14919b", activeforeground="white", padx=20, pady=10)
btn_login.pack(pady=20)

# Etichetta Oppure
label_or = tk.Label(login_window, text="Oppure", bg="#2e2e2e", fg="white", font=("Helvetica", 10))
label_or.pack(pady=5)

# Bottone Registrati
btn_register = tk.Button(login_window, text="Registrati", command=open_registration_window,
                         bg="#14919b", fg="white", font=("Helvetica", 12), activebackground="#0d7377", activeforeground="white", padx=20, pady=10)
btn_register.pack(pady=10)

login_window.mainloop()
