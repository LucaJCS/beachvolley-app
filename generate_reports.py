import sqlite3
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Rectangle
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

# Configurazione matplotlib per evitare problemi di display
matplotlib.use('Agg')

# Dizionario con i limiti di partecipanti per sport
SPORT_LIMITS = {
    "BeachVolley": 8,
    "Tennis": 2,
    "Calcetto": 10,
    "Padel": 4
}

def get_database_path():
    """Ottiene il percorso del database"""
    return os.path.join(os.path.dirname(__file__), 'sports.db')

def get_sport_participants_count():
    """Estrae il numero di partecipanti per sport dal database"""
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    
    sport_counts = {}
    
    for sport in SPORT_LIMITS.keys():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {sport.lower()}")
            count = cursor.fetchone()[0]
            sport_counts[sport] = count
        except Exception as e:
            print(f"Errore nel contare partecipanti per {sport}: {e}")
            sport_counts[sport] = 0
    
    conn.close()
    return sport_counts

def get_event_participants():
    """Estrae i dati degli eventi e i loro partecipanti"""
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    
    event_data = {}
    
    try:
        cursor.execute("SELECT id, sport, event_name, event_date FROM sport_events")
        events = cursor.fetchall()
        
        for event_id, sport, event_name, event_date in events:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {sport.lower()}_event_{event_id}_participants")
                count = cursor.fetchone()[0]
                max_count = SPORT_LIMITS.get(sport, 0)
                
                if sport not in event_data:
                    event_data[sport] = []
                
                event_data[sport].append({
                    'name': event_name,
                    'date': event_date,
                    'participants': count,
                    'max': max_count
                })
            except Exception as e:
                print(f"Errore nel contare partecipanti evento {event_id}: {e}")
    except Exception as e:
        print(f"Errore nel leggere eventi: {e}")
    
    conn.close()
    return event_data

def create_sport_comparison_chart():
    """Crea un grafico a barre che confronta i partecipanti per sport"""
    sport_counts = get_sport_participants_count()
    
    sports = list(sport_counts.keys())
    counts = list(sport_counts.values())
    limits = [SPORT_LIMITS[sport] for sport in sports]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = range(len(sports))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], counts, width, label='Partecipanti Registrati', color='#0d7377', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], limits, width, label='Limite Massimo', color='#ff6b6b', alpha=0.8)
    
    ax.set_xlabel('Sport', fontsize=12, fontweight='bold')
    ax.set_ylabel('Numero di Partecipanti', fontsize=12, fontweight='bold')
    ax.set_title('Confronto Partecipanti per Sport', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(sports, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Aggiungi i valori sopra le barre
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    return fig

def create_sport_pie_chart():
    """Crea un grafico a torta con la distribuzione dei partecipanti"""
    sport_counts = get_sport_participants_count()
    
    sports = list(sport_counts.keys())
    counts = list(sport_counts.values())
    
    # Filtra gli sport con almeno 1 partecipante per il pie chart
    non_zero_sports = [(s, c) for s, c in zip(sports, counts) if c > 0]
    
    if non_zero_sports:
        sports_filtered, counts_filtered = zip(*non_zero_sports)
        
        colors_pie = ['#0d7377', '#14919b', '#ff6b6b', '#feca57']
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(counts_filtered, labels=sports_filtered, autopct='%1.1f%%',
                                           colors=colors_pie[:len(sports_filtered)], startangle=90,
                                           textprops={'fontsize': 11, 'weight': 'bold'})
        
        ax.set_title('Distribuzione Partecipanti per Sport', fontsize=14, fontweight='bold')
        
        # Migliora la leggibilità dei testi
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
        
        plt.tight_layout()
        return fig
    else:
        return None

def create_sport_usage_chart():
    """Crea un grafico che mostra l'utilizzo della capacità per sport"""
    sport_counts = get_sport_participants_count()
    
    sports = list(sport_counts.keys())
    counts = list(sport_counts.values())
    limits = [SPORT_LIMITS[sport] for sport in sports]
    
    # Calcola la percentuale di utilizzo
    usage_percentages = [(c / l * 100) if l > 0 else 0 for c, l in zip(counts, limits)]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors_usage = ['#00ff00' if p <= 50 else '#ffaa00' if p <= 100 else '#ff0000' for p in usage_percentages]
    
    bars = ax.barh(sports, usage_percentages, color=colors_usage, alpha=0.8)
    
    ax.set_xlabel('Percentuale di Utilizzo Capacità (%)', fontsize=12, fontweight='bold')
    ax.set_title('Utilizzo della Capacità per Sport', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 150)
    
    # Aggiungi linea al 100%
    ax.axvline(x=100, color='red', linestyle='--', linewidth=2, label='Capacità Massima')
    
    # Aggiungi i valori sulle barre
    for i, (bar, val) in enumerate(zip(bars, usage_percentages)):
        ax.text(val + 2, i, f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')
    
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    return fig

def create_events_by_sport_table():
    """Crea una tabella con gli eventi per sport"""
    event_data = get_event_participants()
    
    table_data = [['Sport', 'Evento', 'Data', 'Partecipanti', 'Limite']]
    
    for sport in sorted(event_data.keys()):
        events = event_data[sport]
        for event in events:
            table_data.append([
                sport,
                event['name'][:20],  # Limita il nome a 20 caratteri
                event['date'][:10],  # Solo la data
                str(event['participants']),
                str(event['max'])
            ])
    
    return table_data

def generate_pdf_report(filename='report_sportivi.pdf'):
    """Genera un report PDF completo con tutti i grafici"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Titolo del report
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0d7377'),
        spaceAfter=30,
        alignment=1  # Centro
    )
    
    title = Paragraph('Report Statistiche Sportive', title_style)
    story.append(title)
    
    # Data di generazione
    date_text = Paragraph(f'Generato il: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', styles['Normal'])
    story.append(date_text)
    story.append(Spacer(1, 0.3*inch))
    
    # Grafico 1: Confronto partecipanti
    try:
        fig1 = create_sport_comparison_chart()
        if fig1:
            img_buffer1 = io.BytesIO()
            fig1.savefig(img_buffer1, format='png', dpi=100, bbox_inches='tight')
            img_buffer1.seek(0)
            plt.close(fig1)
            
            img1 = Image(img_buffer1, width=6.5*inch, height=3.9*inch)
            story.append(img1)
            story.append(Spacer(1, 0.2*inch))
    except Exception as e:
        print(f"Errore nella creazione del grafico di confronto: {e}")
    
    # Grafico 2: Distribuzione a torta
    try:
        fig2 = create_sport_pie_chart()
        if fig2:
            img_buffer2 = io.BytesIO()
            fig2.savefig(img_buffer2, format='png', dpi=100, bbox_inches='tight')
            img_buffer2.seek(0)
            plt.close(fig2)
            
            img2 = Image(img_buffer2, width=6.5*inch, height=5.2*inch)
            story.append(img2)
            story.append(PageBreak())
    except Exception as e:
        print(f"Errore nella creazione del grafico a torta: {e}")
    
    # Grafico 3: Utilizzo capacità
    try:
        fig3 = create_sport_usage_chart()
        if fig3:
            img_buffer3 = io.BytesIO()
            fig3.savefig(img_buffer3, format='png', dpi=100, bbox_inches='tight')
            img_buffer3.seek(0)
            plt.close(fig3)
            
            img3 = Image(img_buffer3, width=6.5*inch, height=3.9*inch)
            story.append(img3)
            story.append(Spacer(1, 0.2*inch))
    except Exception as e:
        print(f"Errore nella creazione del grafico di utilizzo: {e}")
    
    # Tabella con dettagli eventi
    story.append(PageBreak())
    table_title = Paragraph('Dettaglio Eventi per Sport', title_style)
    story.append(table_title)
    story.append(Spacer(1, 0.2*inch))
    
    try:
        table_data = create_events_by_sport_table()
        if len(table_data) > 1:
            events_table = Table(table_data, colWidths=[1.2*inch, 2*inch, 1*inch, 1.2*inch, 1*inch])
            events_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d7377')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(events_table)
        else:
            story.append(Paragraph('Nessun evento registrato nel database.', styles['Normal']))
    except Exception as e:
        print(f"Errore nella creazione della tabella: {e}")
        story.append(Paragraph(f'Errore nel caricamento dei dati: {str(e)}', styles['Normal']))
    
    # Genera il PDF
    try:
        doc.build(story)
        print(f"✓ Report PDF generato con successo: {filename}")
        return True
    except Exception as e:
        print(f"✗ Errore nella generazione del PDF: {e}")
        return False

def generate_sport_report(sport_name, filename=None):
    """Genera un report PDF per uno sport specifico"""
    
    if filename is None:
        filename = f'report_{sport_name.lower()}.pdf'
    
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0d7377'),
        spaceAfter=30,
        alignment=1
    )
    
    # Titolo
    title = Paragraph(f'Report: {sport_name}', title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Statistiche generali
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {sport_name.lower()}")
        total_players = cursor.fetchone()[0]
        max_capacity = SPORT_LIMITS.get(sport_name, 0)
        usage_percent = (total_players / max_capacity * 100) if max_capacity > 0 else 0
        
        stats_text = f"""
        <b>Statistiche Generali:</b><br/>
        Giocatori Registrati: <b>{total_players}</b><br/>
        Capacità Massima: <b>{max_capacity}</b><br/>
        Utilizzo Capacità: <b>{usage_percent:.1f}%</b><br/>
        """
        
        story.append(Paragraph(stats_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    except Exception as e:
        print(f"Errore nel leggere statistiche per {sport_name}: {e}")
    
    # Eventi per questo sport
    try:
        cursor.execute("SELECT id, event_name, event_date FROM sport_events WHERE sport = ?", (sport_name,))
        events = cursor.fetchall()
        
        if events:
            story.append(Paragraph('<b>Eventi:</b>', styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for event_id, event_name, event_date in events:
                cursor.execute(f"SELECT COUNT(*) FROM {sport_name.lower()}_event_{event_id}_participants")
                participants = cursor.fetchone()[0]
                
                event_info = f"<b>{event_name}</b> ({event_date}) - {participants} partecipanti"
                story.append(Paragraph(event_info, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
    except Exception as e:
        print(f"Errore nel leggere eventi per {sport_name}: {e}")
    
    conn.close()
    
    try:
        doc.build(story)
        print(f"✓ Report per {sport_name} generato: {filename}")
        return True
    except Exception as e:
        print(f"✗ Errore nella generazione del report per {sport_name}: {e}")
        return False

if __name__ == "__main__":
    print("Generazione Report Statistiche Sportive...")
    print("-" * 50)
    
    # Genera il report generale
    generate_pdf_report('report_sportivi.pdf')
    
    # Genera report per ogni sport
    for sport in ["BeachVolley", "Tennis", "Calcetto", "Padel"]:
        generate_sport_report(sport)
    
    print("-" * 50)
    print("Tutti i report sono stati generati!")
