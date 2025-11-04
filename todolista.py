import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os

# ==========================
# 1. MODEL
# ==========================

class Zadatak:
    def __init__(self, opis, rok):
        self.opis = opis
        self.rok = rok
        self.dovrsen = False

    def oznaci_dovrsen(self):
        self.dovrsen = not self.dovrsen

    def __str__(self):
        status = "✓" if self.dovrsen else "✗"
        return f"[{status}] {self.opis} (rok: {self.rok})"


class ObicanZadatak(Zadatak):
    def __init__(self, opis, rok):
        super().__init__(opis, rok)


class PrioritetniZadatak(Zadatak):
    def __init__(self, opis, rok, prioritet):
        super().__init__(opis, rok)
        self.prioritet = prioritet  # "Visok", "Srednji", "Nizak"

    def __str__(self):
        status = "✓" if self.dovrsen else "✗"
        return f"[{status}] {self.opis} (rok: {self.rok}, prioritet: {self.prioritet})"


# ==========================
# 2. APLIKACIJA (GUI)
# ==========================

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proširena To-Do Lista")
        self.zadaci = []

        # --- Okvir za unos ---
        frame_unos = tk.Frame(root)
        frame_unos.pack(pady=10)

        tk.Label(frame_unos, text="Opis zadatka:").grid(row=0, column=0)
        self.entry_opis = tk.Entry(frame_unos, width=30)
        self.entry_opis.grid(row=0, column=1, padx=5)

        tk.Label(frame_unos, text="Rok:").grid(row=1, column=0)
        self.entry_rok = tk.Entry(frame_unos, width=30)
        self.entry_rok.grid(row=1, column=1, padx=5)

        self.var_prioritet = tk.BooleanVar()
        tk.Checkbutton(frame_unos, text="Prioritetni zadatak", variable=self.var_prioritet,
                       command=self.toggle_prioritet).grid(row=2, column=0, columnspan=2, pady=5)

        tk.Label(frame_unos, text="Razina prioriteta:").grid(row=3, column=0)
        self.combo_prioritet = ttk.Combobox(frame_unos, values=["Visok", "Srednji", "Nizak"], state="disabled")
        self.combo_prioritet.grid(row=3, column=1, padx=5)

        tk.Button(frame_unos, text="Dodaj zadatak", command=self.dodaj_zadatak).grid(row=4, column=0, columnspan=2, pady=5)

        # --- Listbox za prikaz zadataka ---
        self.listbox = tk.Listbox(root, width=70, height=12)
        self.listbox.pack(pady=10)
        self.listbox.bind("<Double-Button-1>", self.toggle_dovrsen)

        # --- Gumbi za akcije ---
        frame_gumbi = tk.Frame(root)
        frame_gumbi.pack()

        tk.Button(frame_gumbi, text="Označi dovršenim", command=self.toggle_dovrsen).grid(row=0, column=0, padx=5)
        tk.Button(frame_gumbi, text="Obriši zadatak", command=self.obrisi_zadatak).grid(row=0, column=1, padx=5)
        tk.Button(frame_gumbi, text="Spremi", command=self.spremi_zadatke).grid(row=0, column=2, padx=5)
        tk.Button(frame_gumbi, text="Učitaj", command=self.ucitaj_zadatke).grid(row=0, column=3, padx=5)

    # ==========================
    # LOGIKA
    # ==========================

    def toggle_prioritet(self):
        if self.var_prioritet.get():
            self.combo_prioritet.config(state="readonly")
        else:
            self.combo_prioritet.config(state="disabled")

    def dodaj_zadatak(self):
        opis = self.entry_opis.get().strip()
        rok = self.entry_rok.get().strip()

        if not opis:
            messagebox.showwarning("Upozorenje", "Opis zadatka ne može biti prazan.")
            return

        if self.var_prioritet.get():
            prioritet = self.combo_prioritet.get() or "Srednji"
            zad = PrioritetniZadatak(opis, rok, prioritet)
        else:
            zad = ObicanZadatak(opis, rok)

        self.zadaci.append(zad)
        self.osvjezi_prikaz()
        self.entry_opis.delete(0, tk.END)
        self.entry_rok.delete(0, tk.END)

    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for zad in self.zadaci:
            prikaz = str(zad)
            self.listbox.insert(tk.END, prikaz)
            idx = self.listbox.size() - 1

            # Bojanje po prioritetu
            if isinstance(zad, PrioritetniZadatak):
                if zad.prioritet == "Visok":
                    self.listbox.itemconfig(idx, {'bg': '#ff9999'})
                elif zad.prioritet == "Srednji":
                    self.listbox.itemconfig(idx, {'bg': '#fff2cc'})
                else:
                    self.listbox.itemconfig(idx, {'bg': '#d9ead3'})

            # Precrtavanje ako je dovršen
            if zad.dovrsen:
                self.listbox.itemconfig(idx, {'fg': 'gray', 'font': ('Arial', 10, 'overstrike')})

    def toggle_dovrsen(self, event=None):
        index = self.listbox.curselection()
        if not index:
            return
        idx = index[0]
        self.zadaci[idx].oznaci_dovrsen()
        self.osvjezi_prikaz()

    def obrisi_zadatak(self):
        index = self.listbox.curselection()
        if not index:
            return
        idx = index[0]
        del self.zadaci[idx]
        self.osvjezi_prikaz()

    def spremi_zadatke(self):
        with open("zadaci.pkl", "wb") as f:
            pickle.dump(self.zadaci, f)
        messagebox.showinfo("Spremanje", "Zadaci su uspješno spremljeni!")

    def ucitaj_zadatke(self):
        if not os.path.exists("zadaci.pkl"):
            messagebox.showwarning("Učitavanje", "Datoteka ne postoji!")
            return
        with open("zadaci.pkl", "rb") as f:
            self.zadaci = pickle.load(f)
        self.osvjezi_prikaz()
        messagebox.showinfo("Učitavanje", "Zadaci su učitani.")


# ==========================
# 3. POKRETANJE
# ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
