import customtkinter as ctk
from tkinter import colorchooser, messagebox
import re, os, subprocess, threading, sys, time

class TitanUltimate(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Titan V5 - Ultimate Customizer & Generator")
        self.geometry("1300x950")
        ctk.set_appearance_mode("dark")

        # --- VARIABLES ---
        self.colors = {
            "BG": "#000000", 
            "ACCENT": "#58e58e", 
            "TEXT": "#ffffff", 
            "BORDER": "#58e58e"
        }
        self.font_size = 12
        self.spacing = 26
        self.radius = 8
        self.test_process = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR SCROLLABLE ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=400, fg_color="#101010")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="1. CODE SOURCE", font=("Impact", 20)).pack(pady=10)
        self.code_input = ctk.CTkTextbox(self.sidebar, height=180, font=("Consolas", 10))
        self.code_input.pack(fill="x", padx=15)

        # --- SECTION COULEURS ---
        ctk.CTkLabel(self.sidebar, text="2. COULEURS", font=("Impact", 20)).pack(pady=15)
        self.create_color_btn("FOND (BG)", "BG")
        self.create_color_btn("BOUTONS (ACCENT)", "ACCENT")
        self.create_color_btn("TEXTE", "TEXT")
        self.create_color_btn("ENCADRÉS (BORDER)", "BORDER")

        # --- SECTION TAILLES & EMPLACEMENTS ---
        ctk.CTkLabel(self.sidebar, text="3. TAILLES & DISPOSITION", font=("Impact", 20)).pack(pady=15)
        self.create_slider("Taille du Texte", 8, 40, self.font_size, "font_size")
        self.create_slider("Espacement (Padding)", 0, 60, self.spacing, "spacing")
        self.create_slider("Arrondi des coins", 0, 30, self.radius, "radius")

        # --- BOUTONS D'ACTION ---
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#333").pack(fill="x", pady=20)
        
        self.btn_refresh = ctk.CTkButton(self.sidebar, text="LANCER LE TEST", fg_color="#2ecc71", hover_color="#27ae60", height=40, font=("Arial", 13, "bold"), command=self.run_simulation)
        self.btn_refresh.pack(pady=10, padx=20, fill="x")

        self.btn_gen_code = ctk.CTkButton(self.sidebar, text="GÉNÉRER LE CODE FINI (.py)", fg_color="#e67e22", hover_color="#d35400", height=40, font=("Arial", 13, "bold"), command=self.save_final_code)
        self.btn_gen_code.pack(pady=10, padx=20, fill="x")

        # --- CONSOLE DE DROITE ---
        self.console_frame = ctk.CTkFrame(self, fg_color="#050505")
        self.console_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(self.console_frame, text="LOGS DU SIMULATEUR", font=("Consolas", 14, "bold"), text_color="#58e58e").pack(pady=10)
        self.log_box = ctk.CTkTextbox(self.console_frame, fg_color="transparent", font=("Consolas", 11), text_color="#00ff00")
        self.log_box.pack(expand=True, fill="both", padx=10, pady=10)

    # --- FONCTIONS OUTILS ---
    def create_color_btn(self, label, key):
        btn = ctk.CTkButton(self.sidebar, text=label, fg_color="#333", command=lambda: self.pick_c(key))
        btn.pack(pady=5, padx=20, fill="x")

    def create_slider(self, label, fr, to, start, var_name):
        ctk.CTkLabel(self.sidebar, text=label).pack()
        slider = ctk.CTkSlider(self.sidebar, from_=fr, to=to, command=lambda v: self.set_var(var_name, v))
        slider.set(start)
        slider.pack(pady=5)

    def set_var(self, name, value):
        setattr(self, name, int(value))
        self.auto_refresh()

    def log(self, message):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")

    def pick_c(self, key):
        c = colorchooser.askcolor()[1]
        if c:
            self.colors[key] = c
            self.auto_refresh()

    def auto_refresh(self, _=None):
        if hasattr(self, "_timer"): self.after_cancel(self._timer)
        self._timer = self.after(600, self.run_simulation)

    def generate_modified_code(self):
        code = self.code_input.get("1.0", "end-1c")
        if not code: return None

        new_code = code
        # Couleurs
        new_code = re.sub(r'BG\s*=\s*".*?"', f'BG = "{self.colors["BG"]}"', new_code)
        new_code = re.sub(r'TEXT\s*=\s*".*?"', f'TEXT = "{self.colors["TEXT"]}"', new_code)
        new_code = re.sub(r'SURFACE\s*=\s*".*?"', f'SURFACE = "{self.colors["BG"]}"', new_code)
        new_code = re.sub(r'RAISED\s*=\s*".*?"', f'RAISED = "{self.colors["ACCENT"]}"', new_code)
        new_code = re.sub(r'BORDER\s*=\s*".*?"', f'BORDER = "{self.colors["BORDER"]}"', new_code)
        
        # Disposition
        new_code = re.sub(r"padx=\d+", f"padx={self.spacing}", new_code)
        new_code = re.sub(r"pady=\d+", f"pady={self.spacing}", new_code)
        new_code = re.sub(r"corner_radius=\d+", f"corner_radius={self.radius}", new_code)
        
        # Polices
        new_code = re.sub(r'(\(".*?",\s*)\d+', r'\g<1>' + str(self.font_size), new_code)
        return new_code

    def run_simulation(self):
        code = self.generate_modified_code()
        if not code: return
        if self.test_process: self.test_process.terminate()

        with open("temp_sim.py", "w", encoding="utf-8") as f:
            f.write(code)
        
        self.test_process = subprocess.Popen([sys.executable, "temp_sim.py"])
        self.log("Simulateur relancé avec succès.")

    def save_final_code(self):
        code = self.generate_modified_code()
        if code:
            with open("Titan_Final_Code.py", "w", encoding="utf-8") as f:
                f.write(code)
            messagebox.showinfo("Génération", "Fichier 'Titan_Final_Code.py' créé avec succès !")
            self.log("CODE FINAL GÉNÉRÉ DANS : Titan_Final_Code.py")

if __name__ == "__main__":
    app = TitanUltimate()
    app.mainloop()