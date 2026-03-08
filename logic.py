import requests
import csv
import os
import time
import pandas as pd
from datetime import datetime
import glob

def fix_date(date_val):
    if isinstance(date_val, datetime):
        return date_val.strftime('%d-%m-%Y')
    d_str = str(date_val).replace('.', '-').replace('/', '-').strip()
    if len(d_str) >= 10 and d_str[4] == '-':
        try:
            dt = datetime.strptime(d_str[:10], '%Y-%m-%d')
            return dt.strftime('%d-%m-%Y')
        except: pass
    return d_str

def get_year_from_date(date_str):
    try:
        if '-' in date_str:
            parts = date_str.split('-')
            return int(parts[0]) if len(parts[0]) == 4 else int(parts[2])
    except: return 0
    return 0

def write_to_smart_csv(s, folder):
    artist = s.get('artist', {}).get('name')
    date = s.get('eventDate')
    venue_raw = s.get('venue', {}).get('name', 'Unknown_Venue')
    city = s.get('venue', {}).get('city', {}).get('name', '')
    venue_clean = venue_raw.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filename = f"Setlist_{date}_{venue_clean}.csv"
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Artist', 'Datum', 'Venue', 'City', 'Set Typ', 'Nr', 'Song Name', 'Info'])
        sets = s.get('sets', {}).get('set', [])
        if not sets:
            writer.writerow([artist, date, venue_raw, city, "", "", "Keine Songs eingetragen", ""])
        else:
            for subset in sets:
                label = f"Encore {subset.get('encore')}" if subset.get('encore') else "Main Set"
                for idx, song in enumerate(subset.get('song', []), 1):
                    info = song.get('info', '')
                    if song.get('tape'): info += " (Tape)"
                    writer.writerow([artist, date, venue_raw, city, label, idx, song.get('name'), info])
    return filename

def update_sync_status(folder, excel_row, artist, date, status, last_mod="N/A", csv_path="N/A"):
    status_file = os.path.join(folder, "sync_status.csv")
    cols = ['Excel_Zeile', 'Artist', 'Datum', 'Status', 'Zuletzt_Geaendert', 'CSV_Datei', 'Sync_Datum']
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    new_row = [excel_row, artist, date, status, last_mod, csv_path, now_str]

    if os.path.exists(status_file):
        df = pd.read_csv(status_file, sep=';', encoding='utf-8-sig')
        if excel_row in df['Excel_Zeile'].values:
            df.loc[df['Excel_Zeile'] == excel_row, cols[1:]] = new_row[1:]
        else:
            df = pd.concat([df, pd.DataFrame([new_row], columns=cols)], ignore_index=True)
    else:
        df = pd.DataFrame([new_row], columns=cols)
    df.to_csv(status_file, index=False, sep=';', encoding='utf-8-sig')

def get_sync_status_data(folder):
    status_file = os.path.join(folder, "sync_status.csv")
    if not os.path.exists(status_file): return pd.DataFrame()
    return pd.read_csv(status_file, sep=';', encoding='utf-8-sig')

def get_detailed_stats(folder):
    files = glob.glob(os.path.join(folder, "Setlist_*.csv"))
    if not files: return {"bands": 0, "venues": 0, "concerts": 0}
    data = []
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig', nrows=1)
            if not df.empty: data.append(df.iloc[0].to_dict())
        except: continue
    if not data: return {"bands": 0, "venues": 0, "concerts": 0}
    df_m = pd.DataFrame(data)
    return {"bands": df_m['Artist'].nunique(), "venues": df_m['Venue'].nunique(), "concerts": len(files)}

def get_total_song_count(folder):
    files = glob.glob(os.path.join(folder, "Setlist_*.csv"))
    total = 0
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig')
            total += len(df[df['Song Name'] != "Keine Songs eingetragen"])
        except: continue
    return total

def get_all_artists_from_csvs(folder):
    files = glob.glob(os.path.join(folder, "Setlist_*.csv"))
    artists = set()
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig', nrows=1)
            artists.add(df.iloc[0]['Artist'])
        except: continue
    return sorted(list(artists))

def get_song_stats_for_artist(folder, artist_name):
    files = glob.glob(os.path.join(folder, "Setlist_*.csv"))
    all_songs = []
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig')
            if df.iloc[0]['Artist'].lower() == artist_name.lower():
                songs = df[df['Song Name'] != "Keine Songs eingetragen"]['Song Name'].tolist()
                all_songs.extend(songs)
        except: continue
    return pd.Series(all_songs).value_counts().to_dict() if all_songs else {}
