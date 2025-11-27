import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importa ttk per uno stile più moderno
import sqlite3

# Importa il modulo per la generazione dei report
try:
    from generate_reports import generate_pdf_report
except ImportError:
    generate_pdf_report = None

# Importa componenti GUI e tema
from gui_theme import THEME, FONTS, PADDING, DIMENSIONS
from gui_components import (
    create_window, create_title_label, create_label, create_text_widget,
    create_combobox, create_primary_button, create_secondary_button,
    create_small_button, create_frame, set_text_message, update_text_content,
    create_subtitle_label
)

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
        
        # Crea tabella commenti per l'evento
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {sport.lower()}_event_{event_id}_comments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            comment TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
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
    
    users_window = create_window("Visualizza Utenti", 800, 700)
    users_window_instance = users_window
    
    # Titolo
    label_title = create_title_label(users_window, "Visualizza Utenti")
    label_title.pack(pady=PADDING["large"])
    
    # Sport preferito
    label_sport = create_label(users_window, "Seleziona Sport:")
    label_sport.pack(pady=PADDING["medium"])
    combo_sport_users = create_combobox(users_window, width=30)
    combo_sport_users['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport_users.set("BeachVolley")
    combo_sport_users.pack(pady=PADDING["medium"])
    
    # Area per i risultati
    text_results = create_text_widget(users_window, height=12, width=60)
    text_results.pack(pady=PADDING["medium"], padx=PADDING["medium"])
    
    # Area messaggi
    text_messages = create_text_widget(users_window, height=3, width=60, text_color=THEME["fg_success"])
    text_messages.pack(pady=PADDING["small"], padx=PADDING["medium"])
    
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
                set_text_message(text_messages, f"✓ Utenti caricati: {len(users)}", THEME["fg_success"])
            else:
                text_results.insert(tk.END, f"Nessun utente trovato per {sport}.")
                set_text_message(text_messages, "Nessun utente per questo sport", THEME["fg_warning"])
        except Exception as e:
            text_results.delete(1.0, tk.END)
            set_text_message(text_messages, f"Errore: {str(e)}", THEME["fg_error"])
        conn.close()
    
    # Bottone visualizza
    btn_visualize = create_primary_button(users_window, "Visualizza", command=show_users_from_window)
    btn_visualize.pack(pady=PADDING["large"])
    
    # Carica gli utenti al primo sport
    show_users_from_window()

def open_show_events_window(username):
    global events_window_instance
    
    # Se la finestra è già aperta, portala in primo piano e aggiorna
    if events_window_instance and events_window_instance.winfo_exists():
        events_window_instance.lift()
        events_window_instance.focus()
        return
    
    events_window = create_window("Visualizza Eventi", 1200, 900)
    events_window_instance = events_window
    
    # Titolo
    label_title = create_title_label(events_window, "Visualizza Eventi")
    label_title.pack(pady=PADDING["large"])
    
    # Sport preferito
    label_sport = create_label(events_window, "Seleziona Sport:")
    label_sport.pack(pady=PADDING["medium"])
    combo_sport_events = create_combobox(events_window, width=30)
    combo_sport_events['values'] = ("BeachVolley", "Tennis", "Calcetto", "Padel")
    combo_sport_events.set("BeachVolley")
    combo_sport_events.pack(pady=PADDING["medium"])
    
    # Area per i risultati
    text_results = create_text_widget(events_window, height=10, width=70)
    text_results.pack(pady=PADDING["medium"], padx=PADDING["medium"])
    
    # Selezione evento
    label_select_event = create_label(events_window, "Seleziona Evento:")
    label_select_event.pack(pady=PADDING["medium"])
    combo_events = create_combobox(events_window, width=70)
    combo_events.pack(pady=PADDING["medium"], padx=PADDING["medium"])
    
    # Area messaggi
    text_messages = create_text_widget(events_window, height=2, width=70, text_color=THEME["fg_success"])
    text_messages.pack(pady=PADDING["small"], padx=PADDING["medium"])
    
    # Frame per descrizione e commenti
    frame_details = create_frame(events_window)
    frame_details.pack(pady=PADDING["medium"], padx=PADDING["medium"], fill=tk.BOTH, expand=True)
    
    # Sinistra: Descrizione evento
    frame_left = create_frame(frame_details)
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=PADDING["small"])
    
    label_description = create_subtitle_label(frame_left, "Descrizione Evento:")
    label_description.pack(pady=PADDING["small"])
    text_description = create_text_widget(frame_left, height=15, width=40)
    text_description.pack(pady=PADDING["small"], fill=tk.BOTH, expand=True)
    
    # Destra: Commenti
    frame_right = create_frame(frame_details)
    frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=PADDING["small"])
    
    label_comments = create_subtitle_label(frame_right, "Commenti:")
    label_comments.pack(pady=PADDING["small"])
    text_comments = create_text_widget(frame_right, height=12, width=40, text_color=THEME["fg_info"])
    text_comments.pack(pady=PADDING["small"], fill=tk.BOTH, expand=True)
    
    # Frame per inserire commenti
    frame_new_comment = create_frame(frame_right)
    frame_new_comment.pack(pady=PADDING["small"], fill=tk.X)
    
    label_new_comment = create_label(frame_new_comment, "Nuovo commento:", font_type="smaller")
    label_new_comment.pack(side=tk.LEFT, padx=PADDING["small"])
    
    entry_new_comment = tk.Entry(frame_new_comment, font=FONTS["smaller"], width=25)
    entry_new_comment.pack(side=tk.LEFT, padx=PADDING["small"], fill=tk.X, expand=True)
    
    # Lista per tenere traccia degli event ID
    events_list = []
    current_event_id = None
    current_sport = None
    
    # Funzione per caricare i commenti di un evento
    def load_event_details():
        nonlocal current_event_id, current_sport
        
        if not combo_events.get():
            update_text_content(text_description, "Seleziona un evento per visualizzare i dettagli")
            update_text_content(text_comments, "")
            return
        
        event_num = int(combo_events.get().split(".")[0])
        if event_num < 1 or event_num > len(events_list):
            return
        
        event_id, sport = events_list[event_num - 1]
        current_event_id = event_id
        current_sport = sport
        
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        try:
            # Carica descrizione evento
            cursor.execute("SELECT description FROM sport_events WHERE id = ?", (event_id,))
            result = cursor.fetchone()
            description = result[0] if result and result[0] else "Nessuna descrizione disponibile"
            update_text_content(text_description, description)
            
            # Carica commenti
            cursor.execute(f"SELECT username, comment FROM {sport.lower()}_event_{event_id}_comments ORDER BY timestamp DESC")
            comments = cursor.fetchall()
            
            if comments:
                comments_text = "\n\n".join([f"{username}: {comment}" for username, comment in comments])
            else:
                comments_text = "Nessun commento ancora. Sii il primo a commentare!"
            
            update_text_content(text_comments, comments_text)
        except Exception as e:
            update_text_content(text_description, f"Errore nel caricamento: {str(e)}")
        finally:
            conn.close()
    
    # Aggiorna combo_events con il comando di caricamento dettagli
    combo_events.bind("<<ComboboxSelected>>", lambda e: load_event_details())
    
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
                set_text_message(text_messages, f"✓ {len(events)} eventi trovati", THEME["fg_success"])
            else:
                text_results.insert(tk.END, f"Nessun evento trovato per {sport}.")
                set_text_message(text_messages, "Nessun evento disponibile", THEME["fg_warning"])
        except Exception as e:
            text_results.delete(1.0, tk.END)
            text_results.insert(tk.END, f"Errore: {str(e)}")
            set_text_message(text_messages, f"Errore: {str(e)}", THEME["fg_error"])
        conn.close()
    
    # Funzione per iscriversi all'evento
    def subscribe_to_event():
        try:
            if not combo_events.get():
                set_text_message(text_messages, "✗ Seleziona un evento", THEME["fg_error"])
                return
            
            event_num = int(combo_events.get().split(".")[0])
            if event_num < 1 or event_num > len(events_list):
                set_text_message(text_messages, "✗ Numero evento non valido!", THEME["fg_error"])
                return
            
            event_id, sport = events_list[event_num - 1]
            success, message = register_to_event(sport, event_id, username)
            
            if success:
                show_events_from_window()  # Ricarica gli eventi
                combo_events.set('')
                set_text_message(text_messages, message, THEME["fg_success"])
            else:
                set_text_message(text_messages, message, THEME["fg_error"])
        except (ValueError, IndexError) as e:
            set_text_message(text_messages, f"✗ Errore: {str(e)}", THEME["fg_error"])
    
    # Funzione per aggiungere commento
    def add_comment():
        comment_text = entry_new_comment.get().strip()
        
        if not comment_text:
            set_text_message(text_messages, "✗ Inserisci un commento", THEME["fg_error"])
            return
        
        if not current_event_id or not current_sport:
            set_text_message(text_messages, "✗ Seleziona un evento prima", THEME["fg_error"])
            return
        
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS {current_sport.lower()}_event_{current_event_id}_comments (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL,
                                comment TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            
            cursor.execute(f"INSERT INTO {current_sport.lower()}_event_{current_event_id}_comments (username, comment) VALUES (?, ?)",
                          (username, comment_text))
            conn.commit()
            
            entry_new_comment.delete(0, tk.END)
            load_event_details()  # Ricarica i commenti
            
            set_text_message(text_messages, "✓ Commento aggiunto con successo!", THEME["fg_success"])
        except Exception as e:
            set_text_message(text_messages, f"✗ Errore: {str(e)}", THEME["fg_error"])
        finally:
            conn.close()
    
    # Crea il bottone dopo la definizione della funzione add_comment
    btn_add_comment = create_small_button(frame_new_comment, "Invia", command=add_comment)
    btn_add_comment.pack(side=tk.LEFT, padx=PADDING["small"])
    
    # Bottoni
    button_frame = create_frame(events_window)
    button_frame.pack(pady=PADDING["large"])
    
    btn_visualize = create_primary_button(button_frame, "Visualizza", command=show_events_from_window)
    btn_visualize.pack(side=tk.LEFT, padx=PADDING["medium"])
    
    btn_subscribe = create_secondary_button(button_frame, "Iscriviti", command=subscribe_to_event)
    btn_subscribe.pack(side=tk.LEFT, padx=PADDING["medium"])
    
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
    create_window.geometry("700x600")
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
    
    # Descrizione evento
    label_event_description = tk.Label(create_window, text="Descrizione Evento:", bg="#2e2e2e", fg="white", font=("Helvetica", 12))
    label_event_description.pack(pady=5)
    text_event_description = tk.Text(create_window, height=4, width=35, bg="#1e1e1e", fg="white", font=("Helvetica", 10))
    text_event_description.pack(pady=5)
    
    # Area messaggi
    text_messages = tk.Text(create_window, height=3, width=50, bg="#1e1e1e", fg="#00ff00", font=("Helvetica", 10))
    text_messages.pack(pady=10, padx=10)
    
    # Bottone crea
    def create_event_from_window():
        event_name = entry_event_name.get()
        event_date = entry_event_date.get()
        event_location = entry_event_location.get()
        event_description = text_event_description.get(1.0, tk.END).strip()
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
                    event_location TEXT NOT NULL,
                    description TEXT DEFAULT ''
                )
                ''')
                
                # Aggiungi colonna descrizione se non esiste (retrocompatibilità)
                try:
                    cursor.execute("ALTER TABLE sport_events ADD COLUMN description TEXT DEFAULT ''")
                except sqlite3.OperationalError:
                    pass
                
                cursor.execute("INSERT INTO sport_events (sport, event_name, event_date, event_location, description) VALUES (?, ?, ?, ?, ?)", 
                               (sport, event_name, event_date, event_location, event_description))
                
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
    root.geometry("800x700")
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
    
    # Bottone per generare report
    def generate_report():
        if generate_pdf_report:
            try:
                generate_pdf_report('report_sportivi.pdf')
                messagebox.showinfo("Successo", "Report PDF generato: report_sportivi.pdf")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nella generazione del report: {str(e)}")
        else:
            messagebox.showwarning("Attenzione", "Il modulo generate_reports non è disponibile.")
    
    btn_report = tk.Button(root, text="Genera Report PDF", command=generate_report,
                          bg="#ff6b6b", fg="white", font=("Helvetica", 12), 
                          activebackground="#ff5252", activeforeground="white", padx=30, pady=15, width=25)
    btn_report.pack(pady=10)

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
