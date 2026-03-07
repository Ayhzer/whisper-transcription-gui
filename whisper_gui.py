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

class WhisperApp(BASE):
    def __init__(self):
        super().__init__()
        self.title("Whisper — Transcription Audio")
        self.geometry("820x700"); self.minsize(700,580)
        self.configure(bg=BG); self.resizable(True,True)
        self.audio_path=tk.StringVar(value="")
        self.model_var=tk.StringVar(value="base")
        self.lang_var=tk.StringVar(value="French")
        self.status_var=tk.StringVar(value="En attente d'un fichier audio...")
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
        self.prog=ttk.Progressbar(main,style="AP.Horizontal.TProgressbar",mode="indeterminate")
        self.prog.pack(fill="x",pady=(0,4))
        self.stat_lbl=tk.Label(main,textvariable=self.status_var,font=FONT_SUB,bg=BG,fg=TEXT_DIM,anchor="w")
        self.stat_lbl.pack(fill="x",pady=(0,10))
        self._build_result(main)

    def _build_drop_zone(self,parent):
        outer=tk.Frame(parent,bg=ACCENT,pady=1,padx=1); outer.pack(fill="x",pady=(0,14))
        self.df=tk.Frame(outer,bg=SURFACE2,pady=24,padx=24); self.df.pack(fill="both",expand=True)
        self.di=tk.Label(self.df,text="(( audio ))",font=("Segoe UI",16,"bold"),bg=SURFACE2,fg=ACCENT); self.di.pack()
        dnd_text = "Glissez-deposez votre fichier audio ici" if DND_AVAILABLE else "Cliquez Parcourir pour selectionner un fichier"
        self.dt=tk.Label(self.df,text=dnd_text,font=("Segoe UI",12,"bold"),bg=SURFACE2,fg=TEXT); self.dt.pack(pady=(6,2))
        hint="MP3, WAV, M4A, OGG, FLAC, AAC, WMA..."
        if DND_AVAILABLE: hint = "ou cliquez Parcourir  |  " + hint
        self.dh=tk.Label(self.df,text=hint,font=FONT_SUB,bg=SURFACE2,fg=TEXT_DIM); self.dh.pack()
        self.fn=tk.Label(self.df,text="",font=("Segoe UI",10,"bold"),bg=SURFACE2,fg=SUCCESS); self.fn.pack(pady=(6,0))
        tk.Button(self.df,text="Parcourir...",font=FONT_BTN,bg=SURFACE,fg=TEXT,
            activebackground=BORDER,activeforeground=TEXT,bd=0,padx=18,pady=8,cursor="hand2",
            command=self._browse).pack(pady=(10,0))
        if DND_AVAILABLE:
            for w in (self.df,self.di,self.dt,self.dh,self.fn):
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
        tk.Label(h,text="TRANSCRIPTION",font=FONT_LABEL,bg=BG,fg=TEXT_DIM).pack(side="left")
        tk.Button(h,text="Copier",font=FONT_SUB,bg=SURFACE,fg=TEXT_DIM,activebackground=BORDER,activeforeground=TEXT,bd=0,padx=10,pady=4,cursor="hand2",command=self._copy).pack(side="right")
        tk.Button(h,text="Sauvegarder",font=FONT_SUB,bg=SURFACE,fg=TEXT_DIM,activebackground=BORDER,activeforeground=TEXT,bd=0,padx=10,pady=4,cursor="hand2",command=self._save).pack(side="right",padx=(0,6))
        f=tk.Frame(parent,bg=BORDER,bd=1); f.pack(fill="both",expand=True)
        self.txt=tk.Text(f,font=FONT_MONO,bg=SURFACE,fg=TEXT,insertbackground=ACCENT,relief="flat",bd=0,padx=14,pady=14,wrap="word",selectbackground=ACCENT,selectforeground="white")
        sb=tk.Scrollbar(f,command=self.txt.yview,bg=SURFACE2,troughcolor=SURFACE2,activebackground=ACCENT2,bd=0)
        self.txt.configure(yscrollcommand=sb.set); sb.pack(side="right",fill="y"); self.txt.pack(fill="both",expand=True)
        self.txt.insert("1.0","La transcription apparaitra ici..."); self.txt.configure(state="disabled")

    def _on_enter(self,e):
        [w.configure(bg=DROP_HL) for w in (self.df,self.di,self.dt,self.dh,self.fn)]
    def _on_leave(self,e):
        [w.configure(bg=SURFACE2) for w in (self.df,self.di,self.dt,self.dh,self.fn)]
    def _on_drop(self,e):
        self._on_leave(e)
        path = e.data.strip()
        if path.startswith("{") and path.endswith("}"): path = path[1:-1]
        self._load(path)

    def _center_window(self):
        self.update_idletasks()
        w,h=self.winfo_width(),self.winfo_height()
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _browse(self):
        p=filedialog.askopenfilename(title="Choisir un fichier audio",
            filetypes=[("Fichiers audio","*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.opus"),("Tous","*.*")])
        if p: self._load(p)

    def _load(self,path):
        if os.path.splitext(path)[1].lower() not in AUDIO_EXT:
            messagebox.showwarning("Format non supporte",
                f"'{os.path.basename(path)}' n'est pas un fichier audio reconnu."); return
        self.audio_path.set(path); name=os.path.basename(path)
        self.fn.configure(text=f"[OK]  {name}")
        self.dt.configure(text="Fichier pret a transcrire")
        self.dh.configure(text="Deposez un autre fichier ou cliquez Parcourir pour changer")
        self._setstatus(f"Fichier charge : {name}",TEXT_DIM)

    def _setstatus(self,m,c=TEXT_DIM): self.status_var.set(m); self.stat_lbl.configure(fg=c)
    def _setresult(self,t):
        self.txt.configure(state="normal"); self.txt.delete("1.0","end")
        self.txt.insert("1.0",t); self.txt.configure(state="disabled")

    def _copy(self):
        t=self.txt.get("1.0","end").strip()
        if t and t!="La transcription apparaitra ici...":
            self.clipboard_clear(); self.clipboard_append(t)
            self._setstatus("Texte copie dans le presse-papiers !",SUCCESS)

    def _save(self):
        t=self.txt.get("1.0","end").strip()
        if not t or t=="La transcription apparaitra ici...":
            messagebox.showwarning("Rien a sauvegarder","Lancez d'abord une transcription."); return
        p=filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Fichier texte","*.txt"),("Tous","*.*")],title="Sauvegarder la transcription")
        if p: open(p,"w",encoding="utf-8").write(t); self._setstatus(f"Sauvegarde : {p}",SUCCESS)

    def _start(self):
        path=self.audio_path.get()
        if not path: messagebox.showwarning("Fichier manquant","Selectionnez ou deposez un fichier audio."); return
        if not os.path.isfile(path): messagebox.showerror("Introuvable",f"Fichier introuvable :\n{path}"); return
        if self.is_running: return
        self.is_running=True
        self.btn.configure(state="disabled",bg=SURFACE2,fg=TEXT_DIM,text="Transcription en cours...")
        self.prog.start(12); self._setstatus("Chargement du modele...",ACCENT2); self._setresult("")
        threading.Thread(target=self._whisper,daemon=True).start()

    def _whisper(self):
        path,model,lang=self.audio_path.get(),self.model_var.get(),self.lang_var.get()
        try:
            warnings.filterwarnings("ignore",message="FP16 is not supported on CPU")
            import whisper
            self.after(0,self._setstatus,f"Modele '{model}' en cours de chargement...",ACCENT2)
            m=whisper.load_model(model)
            self.after(0,self._setstatus,"Transcription en cours — patience...",ACCENT2)
            opts={}
            if lang!="Auto": opts["language"]=lang
            r=m.transcribe(path,**opts)
            self.after(0,self._ok,r.get("text","").strip())
        except Exception as e:
            self.after(0,self._err,str(e))

    def _ok(self,text):
        self.is_running=False; self.prog.stop()
        self.btn.configure(state="normal",bg=ACCENT,fg="white",text="Lancer la transcription")
        self._setresult(text)
        self._setstatus(f"Termine — {len(text.split())} mots detectes.",SUCCESS)
        self.stat_lbl.configure(fg=SUCCESS)

    def _err(self,e):
        self.is_running=False; self.prog.stop()
        self.btn.configure(state="normal",bg=ACCENT,fg="white",text="Lancer la transcription")
        self._setresult(f"Erreur :\n\n{e}")
        self._setstatus("Une erreur est survenue.",WARNING)
        self.stat_lbl.configure(fg=WARNING)

if __name__=="__main__":
    WhisperApp().mainloop()
