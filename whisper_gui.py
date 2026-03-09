import sys, os

# S'assurer que les packages utilisateur sont dans le path (fix tkinterdnd2)
_user_site = os.path.join(os.environ.get("APPDATA",""), "Python", "Python314", "site-packages")
if _user_site not in sys.path:
    sys.path.insert(0, _user_site)

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading, warnings

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

BG,SURFACE,SURFACE2 = "#0F0F13","#1A1A23","#22222F"
ACCENT,ACCENT2 = "#7C6EFA","#A598FF"
SUCCESS,WARNING = "#4ECB71","#F5A623"
TEXT,TEXT_DIM,BORDER,DROP_HL = "#E8E6FF","#7B7A9A","#2E2D42","#3D3870"

FONT_TITLE=("Segoe UI",22,"bold"); FONT_SUB=("Segoe UI",10)
FONT_LABEL=("Segoe UI",9,"bold"); FONT_BODY=("Segoe UI",10)
FONT_MONO=("Consolas",10); FONT_BTN=("Segoe UI",10,"bold")
AUDIO_EXT={".mp3",".wav",".m4a",".ogg",".flac",".aac",".wma",".opus"}

BASE = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk

def parse_drop_paths(data):
    """Parse tkinterdnd2 drop data which may contain multiple paths (space or brace-separated)."""
    data = data.strip()
    paths = []
    i = 0
    while i < len(data):
        if data[i] == '{':
            end = data.index('}', i)
            paths.append(data[i+1:end])
            i = end + 1
        else:
            j = i
            while j < len(data) and data[j] != ' ':
                j += 1
            token = data[i:j].strip()
            if token:
                paths.append(token)
            i = j
        while i < len(data) and data[i] == ' ':
            i += 1
    return [p for p in paths if p]

class WhisperApp(BASE):
    def __init__(self):
        super().__init__()
        self.title("Whisper — Transcription Audio")
        self.geometry("820x700"); self.minsize(700,580)
        self.configure(bg=BG); self.resizable(True,True)
        self.audio_paths=[]  # liste de fichiers (batch)
        self.model_var=tk.StringVar(value="base")
        self.lang_var=tk.StringVar(value="French")
        self.status_var=tk.StringVar(value="En attente de fichiers audio...")
        self.is_running=False
        self._build_ui(); self._center_window()

    def _build_ui(self):
        hdr=tk.Frame(self,bg=SURFACE,pady=20); hdr.pack(fill="x")
        tk.Label(hdr,text="Whisper Transcription",font=FONT_TITLE,bg=SURFACE,fg=TEXT).pack(side="left",padx=30)
        tk.Label(hdr,text="Convertissez vos fichiers audio en texte — 100% local",font=FONT_SUB,bg=SURFACE,fg=TEXT_DIM).pack(side="left")
        tk.Frame(self,bg=ACCENT,height=2).pack(fill="x")
        main=tk.Frame(self,bg=BG,padx=30,pady=20); main.pack(fill="both",expand=True)
        self._build_drop_zone(main); self._build_options(main)
        self.btn=tk.Button(main,text="Lancer la transcription",font=FONT_BTN,bg=ACCENT,fg="white",
            activebackground=ACCENT2,activeforeground="white",bd=0,padx=24,pady=12,cursor="hand2",command=self._start)
        self.btn.pack(fill="x",pady=(8,16))
        s=ttk.Style(self); s.theme_use("default")
        s.configure("AP.Horizontal.TProgressbar",troughcolor=SURFACE2,background=ACCENT,thickness=6,borderwidth=0)
        self.prog=ttk.Progressbar(main,style="AP.Horizontal.TProgressbar",mode="determinate")
        self.prog.pack(fill="x",pady=(0,4))
        self.stat_lbl=tk.Label(main,textvariable=self.status_var,font=FONT_SUB,bg=BG,fg=TEXT_DIM,anchor="w")
        self.stat_lbl.pack(fill="x",pady=(0,10))
        self._build_result(main)

    def _build_drop_zone(self,parent):
        outer=tk.Frame(parent,bg=ACCENT,pady=1,padx=1); outer.pack(fill="x",pady=(0,14))
        self.df=tk.Frame(outer,bg=SURFACE2,pady=12,padx=20); self.df.pack(fill="both",expand=True)

        # Ligne du haut : icone + texte + bouton parcourir
        top=tk.Frame(self.df,bg=SURFACE2); top.pack(fill="x")
        self.di=tk.Label(top,text="(( audio ))",font=("Segoe UI",13,"bold"),bg=SURFACE2,fg=ACCENT)
        self.di.pack(side="left")
        dnd_text = "  Glissez vos fichiers ici  |  MP3, WAV, M4A, OGG..." if DND_AVAILABLE else "  Cliquez Parcourir pour selectionner des fichiers"
        self.dt=tk.Label(top,text=dnd_text,font=FONT_SUB,bg=SURFACE2,fg=TEXT_DIM)
        self.dt.pack(side="left",padx=(8,0))
        tk.Button(top,text="Parcourir...",font=FONT_BTN,bg=SURFACE,fg=TEXT,
            activebackground=BORDER,activeforeground=TEXT,bd=0,padx=14,pady=6,cursor="hand2",
            command=self._browse).pack(side="right")

        # Liste des fichiers chargés
        list_frame=tk.Frame(self.df,bg=SURFACE2); list_frame.pack(fill="x",pady=(10,0))
        self.file_listbox=tk.Listbox(list_frame,font=FONT_MONO,bg=SURFACE,fg=SUCCESS,
            selectbackground=ACCENT,selectforeground="white",relief="flat",bd=0,
            height=5,activestyle="none",highlightthickness=0)
        list_sb=tk.Scrollbar(list_frame,command=self.file_listbox.yview,
            bg=SURFACE2,troughcolor=SURFACE2,activebackground=ACCENT2,bd=0,width=10)
        self.file_listbox.configure(yscrollcommand=list_sb.set)
        list_sb.pack(side="right",fill="y"); self.file_listbox.pack(fill="x",expand=True)

        # Barre du bas : compteur + bouton vider
        bot=tk.Frame(self.df,bg=SURFACE2); bot.pack(fill="x",pady=(6,0))
        self.fn=tk.Label(bot,text="Aucun fichier charge",font=FONT_SUB,bg=SURFACE2,fg=TEXT_DIM)
        self.fn.pack(side="left")
        tk.Button(bot,text="Vider la liste",font=FONT_SUB,bg=SURFACE,fg=TEXT_DIM,
            activebackground=BORDER,activeforeground=TEXT,bd=0,padx=10,pady=3,cursor="hand2",
            command=self._clear_files).pack(side="right")

        if DND_AVAILABLE:
            dnd_targets=(self.df,self.di,self.dt,self.file_listbox)
            for w in dnd_targets:
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<Drop>>",self._on_drop)
                w.dnd_bind("<<DragEnter>>",self._on_enter)
                w.dnd_bind("<<DragLeave>>",self._on_leave)

    def _build_options(self,parent):
        row=tk.Frame(parent,bg=BG); row.pack(fill="x",pady=(0,10))
        c1=tk.Frame(row,bg=BG); c1.pack(side="left",fill="x",expand=True,padx=(0,12))
        tk.Label(c1,text="MODELE",font=FONT_LABEL,bg=BG,fg=TEXT_DIM).pack(anchor="w")
        ttk.Combobox(c1,textvariable=self.model_var,values=["tiny","base","small","medium","large"],state="readonly",font=FONT_BODY,width=16).pack(anchor="w",pady=(4,0))
        c2=tk.Frame(row,bg=BG); c2.pack(side="left",fill="x",expand=True,padx=(0,12))
        tk.Label(c2,text="LANGUE",font=FONT_LABEL,bg=BG,fg=TEXT_DIM).pack(anchor="w")
        ttk.Combobox(c2,textvariable=self.lang_var,values=["French","English","Spanish","German","Italian","Portuguese","Dutch","Auto"],state="readonly",font=FONT_BODY,width=16).pack(anchor="w",pady=(4,0))
        c3=tk.Frame(row,bg=BG); c3.pack(side="left",fill="x",expand=True)
        tk.Label(c3,text="CONSEIL",font=FONT_LABEL,bg=BG,fg=TEXT_DIM).pack(anchor="w")
        tk.Label(c3,text="tiny/base = rapide\nmedium/large = precis",font=FONT_SUB,bg=BG,fg=TEXT_DIM,justify="left").pack(anchor="w",pady=(4,0))

    def _build_result(self,parent):
        h=tk.Frame(parent,bg=BG); h.pack(fill="x",pady=(0,6))
        tk.Label(h,text="LOG BATCH",font=FONT_LABEL,bg=BG,fg=TEXT_DIM).pack(side="left")
        tk.Button(h,text="Effacer",font=FONT_SUB,bg=SURFACE,fg=TEXT_DIM,activebackground=BORDER,activeforeground=TEXT,bd=0,padx=10,pady=4,cursor="hand2",command=self._clear_log).pack(side="right")
        f=tk.Frame(parent,bg=BORDER,bd=1); f.pack(fill="both",expand=True)
        self.txt=tk.Text(f,font=FONT_MONO,bg=SURFACE,fg=TEXT,insertbackground=ACCENT,relief="flat",bd=0,padx=14,pady=14,wrap="word",selectbackground=ACCENT,selectforeground="white")
        sb=tk.Scrollbar(f,command=self.txt.yview,bg=SURFACE2,troughcolor=SURFACE2,activebackground=ACCENT2,bd=0)
        self.txt.configure(yscrollcommand=sb.set); sb.pack(side="right",fill="y"); self.txt.pack(fill="both",expand=True)
        self.txt.insert("1.0","Le log de transcription apparaitra ici...\n"); self.txt.configure(state="disabled")

    def _on_enter(self,e):
        [w.configure(bg=DROP_HL) for w in (self.df,self.di,self.dt)]
    def _on_leave(self,e):
        [w.configure(bg=SURFACE2) for w in (self.df,self.di,self.dt)]
    def _on_drop(self,e):
        self._on_leave(e)
        paths = parse_drop_paths(e.data)
        valid = [p for p in paths if os.path.isfile(p) and os.path.splitext(p)[1].lower() in AUDIO_EXT]
        invalid = [p for p in paths if os.path.splitext(p)[1].lower() not in AUDIO_EXT]
        if invalid:
            messagebox.showwarning("Format non supporte",
                f"{len(invalid)} fichier(s) ignore(s) (format non reconnu).")
        if valid:
            self._load_batch(valid)

    def _center_window(self):
        self.update_idletasks()
        w,h=self.winfo_width(),self.winfo_height()
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _browse(self):
        paths=filedialog.askopenfilenames(title="Choisir un ou plusieurs fichiers audio",
            filetypes=[("Fichiers audio","*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.opus"),("Tous","*.*")])
        if paths:
            self._load_batch(list(paths))

    def _load_batch(self, paths):
        # Ajoute sans doublon
        existing = set(self.audio_paths)
        new_paths = [p for p in paths if p not in existing]
        self.audio_paths.extend(new_paths)
        self._refresh_filelist()

    def _refresh_filelist(self):
        n = len(self.audio_paths)
        self.file_listbox.delete(0,"end")
        for i, p in enumerate(self.audio_paths):
            self.file_listbox.insert("end", f"  {i+1:>2}.  {os.path.basename(p)}")
        label = f"{n} fichier(s) charge(s)" if n > 0 else "Aucun fichier charge"
        self.fn.configure(text=label, fg=SUCCESS if n > 0 else TEXT_DIM)
        self._setstatus(f"{n} fichier(s) charge(s), pret a lancer." if n > 0 else "En attente de fichiers audio...", TEXT_DIM)

    def _clear_files(self):
        self.audio_paths = []
        self._refresh_filelist()

    def _setstatus(self,m,c=TEXT_DIM): self.status_var.set(m); self.stat_lbl.configure(fg=c)

    def _log(self, msg, color=TEXT):
        self.txt.configure(state="normal")
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _clear_log(self):
        self.txt.configure(state="normal")
        self.txt.delete("1.0","end")
        self.txt.configure(state="disabled")

    def _start(self):
        if not self.audio_paths:
            messagebox.showwarning("Fichiers manquants","Selectionnez ou deposez des fichiers audio."); return
        missing = [p for p in self.audio_paths if not os.path.isfile(p)]
        if missing:
            messagebox.showerror("Introuvable", f"{len(missing)} fichier(s) introuvable(s).\nVerifiez les chemins."); return
        if self.is_running: return
        self.is_running=True
        self.btn.configure(state="disabled",bg=SURFACE2,fg=TEXT_DIM,text="Batch en cours...")
        self.prog.configure(mode="determinate", value=0, maximum=len(self.audio_paths))
        self._setstatus("Chargement du modele...",ACCENT2)
        self._clear_log()
        threading.Thread(target=self._whisper_batch, daemon=True).start()

    def _whisper_batch(self):
        paths = self.audio_paths
        model_name = self.model_var.get()
        lang = self.lang_var.get()
        n = len(paths)
        try:
            warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
            import whisper, ssl
            # Fix SSL certificate verify failed sur certains environnements Windows
            ssl._create_default_https_context = ssl._create_unverified_context
            self.after(0, self._setstatus, f"Chargement du modele '{model_name}'...", ACCENT2)
            model = whisper.load_model(model_name)
            self.after(0, self._log, f"Modele '{model_name}' charge. {n} fichier(s) a traiter.\n{'='*50}")
            ok_count = 0
            err_count = 0
            for i, path in enumerate(paths):
                name = os.path.basename(path)
                self.after(0, self._setstatus, f"[{i+1}/{n}] Transcription : {name}", ACCENT2)
                self.after(0, self._log, f"\n[{i+1}/{n}] {name}")
                try:
                    opts = {}
                    if lang != "Auto": opts["language"] = lang
                    result = model.transcribe(path, **opts)
                    text = result.get("text", "").strip()
                    # Sauvegarde automatique .txt au meme endroit
                    txt_path = os.path.splitext(path)[0] + ".txt"
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    words = len(text.split())
                    self.after(0, self._log, f"  OK  {words} mots → {os.path.basename(txt_path)}")
                    ok_count += 1
                except Exception as e:
                    self.after(0, self._log, f"  ERREUR : {e}")
                    err_count += 1
                self.after(0, self._prog_step, i+1)
            self.after(0, self._batch_done, ok_count, err_count, n)
        except Exception as e:
            self.after(0, self._err, str(e))

    def _prog_step(self, val):
        self.prog.configure(value=val)

    def _batch_done(self, ok, err, total):
        self.is_running = False
        self.btn.configure(state="normal", bg=ACCENT, fg="white", text="Lancer la transcription")
        summary = f"\n{'='*50}\nBatch termine : {ok}/{total} reussis"
        if err: summary += f", {err} erreur(s)"
        self.after(0, self._log, summary)
        color = SUCCESS if err == 0 else WARNING
        self._setstatus(f"Batch termine — {ok}/{total} fichiers transcrits.", color)
        self.stat_lbl.configure(fg=color)

    def _err(self, e):
        self.is_running = False
        self.prog.configure(value=0)
        self.btn.configure(state="normal", bg=ACCENT, fg="white", text="Lancer la transcription")
        self.after(0, self._log, f"ERREUR FATALE : {e}")
        self._setstatus("Une erreur est survenue.", WARNING)
        self.stat_lbl.configure(fg=WARNING)

if __name__=="__main__":
    WhisperApp().mainloop()
