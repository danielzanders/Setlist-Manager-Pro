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
        self.root.geometry("1000x850")
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
        tk.Label(self.main_container, text="🤘 Konzert Archiv", font=("Arial", 28, "bold"), pady=20).pack()

        s_frame = tk.Frame(self.main_container); s_frame.pack(fill="x", padx=40)
        if os.path.exists(conf.get('folder', '')):
            stats = logic.get_detailed_stats(conf['folder'])
            songs = logic.get_total_song_count(conf['folder'])
            cards = [("Konzerte", stats['concerts'], "#6f42c1"), ("Bands", stats['bands'], "#28a745"), 
                     ("Venues", stats['venues'], "#007bff"), ("Songs", songs, "#fd7e14")]
            for t, v, c in cards:
                f = tk.Frame(s_frame, bg=c, padx=20, pady=15); f.pack(side=tk.LEFT, padx=10, expand=True, fill="both")
                tk.Label(f, text=str(v), font=("Arial", 20, "bold"), bg=c, fg="white").pack()
                tk.Label(f, text=t, font=("Arial", 9), bg=c, fg="white").pack()

        btn_f = tk.Frame(self.main_container, pady=30); btn_f.pack()
        style = {"font": ("Arial", 12, "bold"), "width": 35, "pady": 10, "bg": "#f8f9fa", "cursor": "hand2"}
        tk.Button(btn_f, text="📊 Band- & Song-Analyse", command=self.show_song_analysis, **style).pack(pady=5)
        tk.Button(btn_f, text="🔍 Sync-Status & Fehler", command=self.show_status_overview, **style).pack(pady=5)
        tk.Button(btn_f, text="🔄 Neue Excel-Daten syncen", command=self.show_sync, **style).pack(pady=5)
        tk.Button(btn_f, text="⚙️ Einstellungen", command=self.show_configuration, **style).pack(pady=5)

    def auto_check_new_entries(self):
        conf = cfg.load_config()
        if not os.path.exists(conf.get('excel_path', '')): return
        try:
            df = pd.read_excel(conf['excel_path'])
            if len(df) > int(conf.get('last_line_count', 0)):
                if messagebox.askyesno("Neue Daten", f"Gefunden: {len(df)} Zeilen. Sync starten?"): self.show_sync()
        except: pass

    def show_status_overview(self):
        self.clear_window()
        conf = cfg.load_config()
        tk.Button(self.main_container, text="⬅ Dashboard", command=self.show_dashboard).pack(anchor="w", padx=20, pady=10)
        tk.Label(self.main_container, text="Sync-Status & Fehlersuche", font=("Arial", 18, "bold")).pack()

        f_frame = tk.Frame(self.main_container, pady=10); f_frame.pack()
        v_filter = tk.StringVar(value="Alle")
        opt = ["Alle", "Erfolgreich", "Nicht gefunden", "Keine Songs"]
        tk.OptionMenu(f_frame, v_filter, *opt, command=lambda x: refresh()).pack(side="left", padx=10)

        columns = ("Z", "A", "D", "S")
        tree = ttk.Treeview(self.main_container, columns=columns, show="headings")
        titles = {"Z": "Excel-Zeile", "A": "Band", "D": "Datum", "S": "Status"}
        for c, t in titles.items():
            tree.heading(c, text=t, command=lambda _c=c: sort_col(_c, False))
            tree.column(c, width=100 if c in ["Z", "D"] else 250)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        def sort_col(col, rev):
            l = [(tree.set(k, col), k) for k in tree.get_children('')]
            if col == "Z": l.sort(key=lambda t: int(t[0]), reverse=rev)
            else: l.sort(reverse=rev)
            for i, (v, k) in enumerate(l): tree.move(k, '', i)
            tree.heading(col, command=lambda: sort_col(col, not rev))

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            df = logic.get_sync_status_data(conf['folder'])
            if df.empty: return
            f = v_filter.get()
            if f == "Nicht gefunden": df = df[df['Status'].str.contains("Nicht gefunden", case=False, na=False)]
            elif f != "Alle": df = df[df['Status'] == f]
            for _, r in df.sort_values("Excel_Zeile").iterrows():
                tree.insert("", "end", values=(int(r['Excel_Zeile']), r['Artist'], r['Datum'], r['Status']))
        refresh()

    def show_song_analysis(self):
        self.clear_window()
        conf = cfg.load_config()
        tk.Button(self.main_container, text="⬅ Zurück", command=self.show_dashboard).pack(anchor="w", padx=20, pady=10)
        search_f = tk.Frame(self.main_container, pady=10); search_f.pack()
        arts = logic.get_all_artists_from_csvs(conf['folder'])
        combo = ttk.Combobox(search_f, values=arts, width=30, font=("Arial", 12))
        combo.pack(side="left", padx=10)
        tree = ttk.Treeview(self.main_container, columns=("S", "C"), show="headings")
        tree.heading("S", text="Song"); tree.heading("C", text="Anzahl"); tree.pack(fill="both", expand=True, padx=20)
        def analyze(e=None):
            for i in tree.get_children(): tree.delete(i)
            res = logic.get_song_stats_for_artist(conf['folder'], combo.get())
            for s, c in sorted(res.items(), key=lambda x: x[1], reverse=True):
                tree.insert("", "end", values=(s, f"{c}x"))
        combo.bind("<<ComboboxSelected>>", analyze)
        tk.Button(search_f, text="Analyse", command=analyze).pack(side="left")

    def show_sync(self):
        self.clear_window()
        conf = cfg.load_config()
        tk.Label(self.main_container, text="Synchronisations-Optionen", font=("Arial", 18, "bold"), pady=10).pack()
        f_frame = tk.LabelFrame(self.main_container, text=" Zeitraum ", padx=20, pady=10); f_frame.pack(pady=10)
        tk.Label(f_frame, text="Nur ab Jahr:").pack(side="left")
        y_var = tk.StringVar(value="1990")
        tk.Spinbox(f_frame, from_=1990, to=2026, textvariable=y_var, width=10).pack(side="left", padx=10)
        pb = ttk.Progressbar(self.main_container, length=600, mode='determinate'); pb.pack(pady=5)
        count_lbl = tk.Label(self.main_container, text="Bereit zum Start...", font=("Arial", 10)); count_lbl.pack()
        t_frame = tk.Frame(self.main_container); t_frame.pack(fill="both", expand=True, padx=20, pady=10)
        txt = tk.Text(t_frame, height=12, font=("Consolas", 10)); txt.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(t_frame, command=txt.yview); sb.pack(side="right", fill="y"); txt.config(yscrollcommand=sb.set)

        def run():
            try:
                start_y = int(y_var.get())
                df = pd.read_excel(conf['excel_path'])
                c_d = next((c for c in df.columns if "datum" in c.lower()), None)
                c_a = next((c for c in df.columns if any(x in c.lower() for x in ["band", "artist"])), None)
                df['t_y'] = df[c_d].apply(lambda x: logic.get_year_from_date(logic.fix_date(x)))
                sync_df = df[df['t_y'] >= start_y].copy()
                pb['maximum'] = len(sync_df)
                for i, (idx, row) in enumerate(sync_df.iterrows(), 1):
                    art, dat = str(row[c_a]).strip(), logic.fix_date(row[c_d])
                    count_lbl.config(text=f"Verarbeite {i} von {len(sync_df)}")
                    txt.insert("end", f"[{i}/{len(sync_df)}] Suche: {art} ({dat})...\n"); txt.see("end"); self.root.update()
                    r = requests.get(f"https://api.setlist.fm/rest/1.0/search/setlists?artistName={requests.utils.quote(art)}&date={dat}",
                                     headers={'x-api-key': conf['key'], 'Accept': 'application/json'})
                    if r.status_code == 200:
                        d = r.json().get('setlist', [])[0]
                        fn = logic.write_to_smart_csv(d, conf['folder'])
                        s = "Erfolgreich" if d.get('sets', {}).get('set') else "Keine Songs"
                        logic.update_sync_status(conf['folder'], idx+2, art, dat, s, d.get('lastUpdated'), fn)
                        txt.insert("end", f"   -> {s} ✓\n", "success")
                    else:
                        logic.update_sync_status(conf['folder'], idx+2, art, dat, f"Nicht gefunden ({r.status_code})")
                        txt.insert("end", f"   -> Fehler {r.status_code}\n", "error")
                    txt.tag_config("success", foreground="green"); txt.tag_config("error", foreground="red")
                    pb['value'] = i
                    time.sleep(0.6)
                cfg.save_config(conf['key'], conf['folder'], conf['excel_path'], True, len(df))
                messagebox.showinfo("Done", "Sync fertig!"); self.show_dashboard()
            except Exception as e: messagebox.showerror("Fehler", str(e))
        tk.Button(self.main_container, text="Start Sync", bg="#6f42c1", fg="white", command=run).pack(pady=10)

    def show_configuration(self):
        self.clear_window()
        d = cfg.load_config()
        f = tk.Frame(self.main_container, padx=50, pady=20); f.pack(fill="both")
        tk.Label(f, text="API Key:").pack(anchor="w")
        e_k = tk.Entry(f, width=60); e_k.insert(0, d.get('key','')); e_k.pack(pady=5)
        l_e = tk.Label(f, text=d.get('excel_path', 'Nicht gewählt'), fg="blue"); l_e.pack(anchor="w")
        tk.Button(f, text="Excel wählen", command=lambda: l_e.config(text=filedialog.askopenfilename())).pack(anchor="w")
        l_f = tk.Label(f, text=d.get('folder', 'Nicht gewählt'), fg="blue"); l_f.pack(anchor="w")
        tk.Button(f, text="CSV Ordner wählen", command=lambda: l_f.config(text=filedialog.askdirectory())).pack(anchor="w")
        tk.Button(self.main_container, text="Speichern", bg="#007bff", fg="white", 
                  command=lambda: [cfg.save_config(e_k.get(), l_f.cget("text"), l_e.cget("text"), True, d.get('last_line_count',0)), self.show_dashboard()]).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk(); app = SetlistApp(root); root.mainloop()
