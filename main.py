import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import config_manager as cfg
import logic
import os, requests, time, warnings
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

class SetlistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setlist.fm Manager Pro")
        self.root.geometry("1000x800")
        
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        if not cfg.is_config_complete():
            self.show_configuration()
        else:
            self.show_dashboard()
            self.root.after(1000, self.auto_check_new_entries)

    def clear_window(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def show_dashboard(self):
        self.clear_window()
        conf = cfg.load_config()
        tk.Label(self.main_container, text="🤘 Konzert Archiv Dashboard", font=("Arial", 26, "bold"), pady=20).pack()

        stats_frame = tk.LabelFrame(self.main_container, text=" Deine Live-Statistik ", padx=15, pady=15)
        stats_frame.pack(fill="x", padx=40, pady=10)

        if "folder" in conf and os.path.exists(conf['folder']):
            s = logic.get_detailed_stats(conf['folder'])
            total_songs = logic.get_total_song_count(conf['folder'])
            
            card_container = tk.Frame(stats_frame)
            card_container.pack(pady=10)

            def make_card(parent, title, val, color):
                f = tk.Frame(parent, bg=color, padx=20, pady=15); f.pack(side=tk.LEFT, padx=10)
                tk.Label(f, text=str(val), font=("Arial", 22, "bold"), bg=color, fg="white").pack()
                tk.Label(f, text=title, font=("Arial", 9), bg=color, fg="white").pack()

            make_card(card_container, "Konzerte", s['concerts'], "#6f42c1")
            make_card(card_container, "Bands", s['bands'], "#28a745")
            make_card(card_container, "Venues", s['venues'], "#007bff")
            make_card(card_container, "Songs", total_songs, "#fd7e14")

        btn_frame = tk.Frame(self.main_container, pady=30)
        btn_frame.pack(fill="both", expand=True)
        style = {"font": ("Arial", 12, "bold"), "width": 40, "pady": 12, "bg": "#f8f9fa", "cursor": "hand2"}
        
        tk.Button(btn_frame, text="📊 Band- & Song-Analyse", command=self.show_song_analysis, **style).pack(pady=5)
        tk.Button(btn_frame, text="🔄 Excel Synchronisation", command=self.show_sync, **style).pack(pady=5)
        tk.Button(btn_frame, text="⚙️ Konfiguration", command=self.show_configuration, **style).pack(pady=5)

    def auto_check_new_entries(self):
        conf = cfg.load_config()
        if not os.path.exists(conf.get('excel_path', '')): return
        try:
            df = pd.read_excel(conf['excel_path'])
            if len(df) > int(conf.get('last_line_count', 0)):
                if messagebox.askyesno("Neu", "Neue Einträge in Excel gefunden. Sync starten?"): self.show_sync()
        except: pass

    def show_song_analysis(self):
        self.clear_window()
        conf = cfg.load_config()
        folder = conf.get('folder', '')
        
        nav = tk.Frame(self.main_container, pady=10); nav.pack(fill="x", padx=20)
        tk.Button(nav, text="⬅ Dashboard", command=self.show_dashboard).pack(side="left")
        
        tk.Label(self.main_container, text="Band- & Song-Analyse", font=("Arial", 20, "bold")).pack()
        
        search_f = tk.Frame(self.main_container, pady=20); search_f.pack()
        tk.Label(search_f, text="Band wählen:").pack(side="left")
        
        artist_list = logic.get_all_artists_from_csvs(folder)
        combo = ttk.Combobox(search_f, values=artist_list, width=35, font=("Arial", 11))
        combo.pack(side="left", padx=10)

        tree_f = tk.Frame(self.main_container); tree_f.pack(fill="both", expand=True, padx=40, pady=10)
        tree = ttk.Treeview(tree_f, columns=("S", "A"), show="headings")
        tree.heading("S", text="Song Titel"); tree.heading("A", text="Häufigkeit")
        tree.pack(side="left", fill="both", expand=True)
        
        def update_list(event=None):
            for i in tree.get_children(): tree.delete(i)
            stats = logic.get_song_stats_for_artist(folder, combo.get())
            for s, c in sorted(stats.items(), key=lambda x: x[1], reverse=True):
                tree.insert("", "end", values=(s, f"{c}x"))

        combo.bind("<<ComboboxSelected>>", update_list)
        tk.Button(search_f, text="Anzeigen", command=update_list).pack(side="left")

    def show_sync(self):
        self.clear_window()
        conf = cfg.load_config()
        tk.Label(self.main_container, text="Synchronisation", font=("Arial", 18, "bold"), pady=20).pack()
        pb = ttk.Progressbar(self.main_container, length=700, mode='determinate'); pb.pack(pady=10)
        txt = tk.Text(self.main_container, height=15, width=90); txt.pack(pady=10)

        def run():
            try:
                df = pd.read_excel(conf['excel_path'])
                c_date = next((c for c in df.columns if "datum" in c.lower()), None)
                c_art = next((c for c in df.columns if any(x in c.lower() for x in ["band", "artist"])), None)
                pb['maximum'] = len(df)
                for i, row in df.iterrows():
                    art, dat = str(row[c_art]).strip(), logic.fix_date(row[c_date])
                    txt.insert("end", f"Check: {art}...\n"); txt.see("end"); self.root.update()
                    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistName={requests.utils.quote(art)}&date={dat}"
                    r = requests.get(url, headers={'x-api-key': conf['key'], 'Accept': 'application/json'})
                    if r.status_code == 200: logic.write_to_smart_csv(r.json().get('setlist', [])[0], conf['folder'])
                    pb['value'] = i + 1
                    time.sleep(0.6)
                cfg.save_config(conf['key'], conf['folder'], conf['excel_path'], True, len(df))
                messagebox.showinfo("Ready", "Sync fertig!"); self.show_dashboard()
            except Exception as e: messagebox.showerror("Error", str(e)); self.show_dashboard()

        tk.Button(self.main_container, text="Start", bg="#6f42c1", fg="white", command=run).pack(pady=10)

    def show_configuration(self):
        self.clear_window()
        d = cfg.load_config()
        tk.Label(self.main_container, text="Einstellungen", font=("Arial", 20, "bold"), pady=30).pack()
        f = tk.Frame(self.main_container, padx=60); f.pack(fill="x")
        tk.Label(f, text="API Key:").pack(anchor="w")
        e_key = tk.Entry(f, width=70); e_key.insert(0, d.get('key','')); e_key.pack(pady=10)
        
        l_ex = tk.Label(f, text=d.get('excel_path', 'Nicht gewählt'), fg="blue"); l_ex.pack(anchor="w")
        tk.Button(f, text="Excel wählen", command=lambda: l_ex.config(text=filedialog.askopenfilename())).pack(anchor="w")
        
        l_fo = tk.Label(f, text=d.get('folder', 'Nicht gewählt'), fg="blue"); l_fo.pack(anchor="w")
        tk.Button(f, text="Ordner wählen", command=lambda: l_fo.config(text=filedialog.askdirectory())).pack(anchor="w")
        
        tk.Button(self.main_container, text="Speichern", bg="#007bff", fg="white", 
                  command=lambda: [cfg.save_config(e_key.get(), l_fo.cget("text"), l_ex.cget("text"), True, d.get('last_line_count',0)), self.show_dashboard()]).pack(pady=40)

if __name__ == "__main__":
    root = tk.Tk(); app = SetlistApp(root); root.mainloop()