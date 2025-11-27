import sqlite3
from rich.console import Console
from rich.table import Table

# Inizializza la console rich
console = Console()

def show_users():
    sport = input("Seleziona lo sport (BeachVolley, Tennis, Calcetto, Padel): ")
    level = input("Seleziona il livello (Principiante, Intermedio, Avanzato): ")

    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {sport.lower()} WHERE level = ?", (level,))
    users = cursor.fetchall()
    
    if users:
        table = Table(show_header=True, header_style="bold magenta", title=f"Utenti per {sport} - {level}")
        table.add_column("ID", justify="right")
        table.add_column("Nome", justify="center")
        table.add_column("Livello", justify="center")
        
        for user in users:
            table.add_row(str(user[0]), user[1], user[2])
        
        console.print(table)
    else:
        console.print(f"[bold red]Nessun utente trovato per {sport} e {level}.[/bold red]")

    conn.close()

def create_event():
    event_name = input("Nome dell'evento: ")
    event_date = input("Data dell'evento (AAAA-MM-GG): ")
    event_location = input("Location dell'evento: ")
    sport = input("Sport dell'evento (BeachVolley, Tennis, Calcetto, Padel): ")

    if event_name and event_date and event_location:
        conn = sqlite3.connect('sports.db')
        cursor = conn.cursor()

        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {sport.lower()}_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_location TEXT NOT NULL
        )
        ''')

        cursor.execute(f"INSERT INTO {sport.lower()}_events (event_name, event_date, event_location) VALUES (?, ?, ?)", 
                       (event_name, event_date, event_location))

        conn.commit()
        conn.close()

        console.print(f"[bold green]L'evento '{event_name}' è stato creato con successo![/bold green]")
    else:
        console.print("[bold red]Errore! Completa tutti i campi![/bold red]")

def show_events():
    sport = input("Seleziona lo sport per gli eventi (BeachVolley, Tennis, Calcetto, Padel): ")
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {sport.lower()}_events")
    events = cursor.fetchall()

    if events:
        table = Table(show_header=True, header_style="bold blue", title=f"Eventi per {sport}")
        table.add_column("ID", justify="right")
        table.add_column("Nome Evento", justify="center")
        table.add_column("Data Evento", justify="center")
        table.add_column("Location", justify="center")

        for event in events:
            table.add_row(str(event[0]), event[1], event[2], event[3])

        console.print(table)
    else:
        console.print(f"[bold red]Nessun evento trovato per {sport}.[/bold red]")

    conn.close()

def stats_events_by_sport():
    sport = input("Seleziona lo sport (BeachVolley, Tennis, Calcetto, Padel): ")

    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {sport.lower()}_events")
    count = cursor.fetchone()[0]

    console.print(f"[bold yellow]Numero di eventi per {sport}: {count}[/bold yellow]")
    conn.close()

def stats_users_by_sport():
    sport = input("Seleziona lo sport (BeachVolley, Tennis, Calcetto, Padel): ")

    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {sport.lower()}")
    count = cursor.fetchone()[0]

    console.print(f"[bold yellow]Numero di utenti per {sport}: {count}[/bold yellow]")
    conn.close()

# Menu principale
def main():
    console.print("[bold blue]Benvenuto nell'app per la gestione degli eventi sportivi![/bold blue]")
    while True:
        console.print("\n[bold green]1. Cerca Utenti per Sport e Livello[/bold green]")
        console.print("[bold green]2. Crea Evento[/bold green]")
        console.print("[bold green]3. Mostra Eventi[/bold green]")
        console.print("[bold green]4. Statistiche Eventi per Sport[/bold green]")
        console.print("[bold green]5. Statistiche Utenti per Sport[/bold green]")
        console.print("[bold red]6. Esci[/bold red]")

        choice = input("\nScegli un'opzione: ")

        if choice == '1':
            show_users()
        elif choice == '2':
            create_event()
        elif choice == '3':
            show_events()
        elif choice == '4':
            stats_events_by_sport()
        elif choice == '5':
            stats_users_by_sport()
        elif choice == '6':
            console.print("[bold red]Uscita dal programma...[/bold red]")
            break
        else:
            console.print("[bold red]Opzione non valida![/bold red]")

if __name__ == "__main__":
    main()
