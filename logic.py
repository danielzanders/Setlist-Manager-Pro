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

def write_to_smart_csv(s, folder):
    artist = s.get('artist', {}).get('name')
    artist_id = s.get('artist', {}).get('mbid', 'N/A')
    date = s.get('eventDate')
    venue_raw = s.get('venue', {}).get('name')
    venue_id = s.get('venue', {}).get('id', 'N/A')
    city = s.get('venue', {}).get('city', {}).get('name', '')
    
    venue_clean = venue_raw.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filepath = os.path.join(folder, f"Setlist_{date}_{venue_clean}.csv")
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Artist', 'Artist_ID', 'Datum', 'Venue', 'Venue_ID', 'City', 'Set Typ', 'Nr', 'Song Name', 'Info'])
        sets = s.get('sets', {}).get('set', [])
        if not sets:
            writer.writerow([artist, artist_id, date, venue_raw, venue_id, city, "", "", "Keine Songs eingetragen", ""])
        else:
            for subset in sets:
                label = f"Encore {subset.get('encore')}" if subset.get('encore') else "Main Set"
                for idx, song in enumerate(subset.get('song', []), 1):
                    info = song.get('info', '')
                    if song.get('tape'): info += " (Tape)"
                    writer.writerow([artist, artist_id, date, venue_raw, venue_id, city, label, idx, song.get('name'), info])
    return True

def get_detailed_stats(folder):
    if not os.path.exists(folder): return {"bands": 0, "venues": 0, "concerts": 0, "top_3": {}}
    files = glob.glob(os.path.join(folder, "*.csv"))
    if not files: return {"bands": 0, "venues": 0, "concerts": 0, "top_3": {}}
    concert_data = []
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig', nrows=1)
            if not df.empty: concert_data.append(df.iloc[0].to_dict())
        except: continue
    if not concert_data: return {"bands": 0, "venues": 0, "concerts": 0, "top_3": {}}
    main_df = pd.DataFrame(concert_data)
    return {
        "bands": main_df['Artist'].nunique(),
        "venues": main_df['Venue'].nunique(),
        "concerts": len(files),
        "top_3": main_df['Artist'].value_counts().head(3).to_dict()
    }

def get_total_song_count(folder):
    files = glob.glob(os.path.join(folder, "*.csv"))
    total = 0
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig')
            total += len(df[df['Song Name'] != "Keine Songs eingetragen"])
        except: continue
    return total

def get_all_artists_from_csvs(folder):
    if not os.path.exists(folder): return []
    files = glob.glob(os.path.join(folder, "*.csv"))
    artists = set()
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig', nrows=1)
            if 'Artist' in df.columns: artists.add(df.iloc[0]['Artist'])
        except: continue
    return sorted(list(artists))

def get_song_stats_for_artist(folder, artist_name):
    files = glob.glob(os.path.join(folder, "*.csv"))
    all_songs = []
    for f in files:
        try:
            df = pd.read_csv(f, sep=';', encoding='utf-8-sig')
            artist_df = df[df['Artist'].str.lower() == artist_name.lower()]
            songs = artist_df[artist_df['Song Name'] != "Keine Songs eingetragen"]['Song Name'].tolist()
            all_songs.extend(songs)
        except: continue
    return pd.Series(all_songs).value_counts().to_dict() if all_songs else {}