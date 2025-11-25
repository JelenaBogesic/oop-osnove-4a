import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os


# ==========================
# MODEL
# ==========================

class Zadatak:
    def __init__(self, opis, rok, prioritet="Srednji", roditelj=None):
        self.opis = opis
        self.rok = datetime.strptime(rok, "%Y-%m-%d") if isinstance(rok, str) else rok
        self.prioritet = prioritet
        self.roditelj = roditelj
        self.podzadaci = []
        self.dovrsen = False

    def oznaci_dovrsen(self, stanje=None):
        if stanje is None:
            self.dovrsen = not self.dovrsen
        else:
            self.dovrsen = stanje
        for pz in self.podzadaci:
            pz.oznaci_dovrsen(self.dovrsen)

    def dodaj_podzadatak(self, podzadatak):
        self.podzadaci.append(podzadatak)
        podzadatak.roditelj = self


# ==========================
# APLIKACIJA
# ==========================

class TaskFlowPro:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow Pro – Upravljanje zadacima")

        self.zadaci = []  # lista glavnih zadataka

        # --- Gornji okvir ---
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Opis:").grid(row=0, column=0, padx=5)
        self.opis_entry = tk.Entry(frame, width=30)
        self.opis_entry.grid(row=0, column=1)

        tk.Label(frame, text="Rok (YYYY-MM-DD):").grid(row=1, column=0)
        self.rok_entry = tk.Entry(frame, width=30)
        self.rok_entry.grid(row=1, column=1)

        tk.Label(frame, text="Prioritet:").grid(row=2, column=0)
        self.prioritet_cb = ttk.Combobox(frame, values=["Visok", "Srednji", "Nizak"], state="readonly", width=27)
        self.prioritet_cb.set("Srednji")
        self.prioritet_cb.grid(row=2, column=1)

        tk.Button(frame, text="Dodaj zadatak", command=self.dodaj_zadatak).grid(row=3, column=0, columnspan=2, pady=5)

        # --- Treeview ---
        self.tree = ttk.Treeview(root, columns=("rok", "prioritet"), show="tree headings")
        self.tree.heading("#0", text="Zadatak")
        self.tree.heading("rok", text="Rok")
        self.tree.heading("prioritet", text="Prioritet")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree.bind("<Double-Button-1>", self.toggle_dovrsen)

        # --- Gumbi ---
        gumbi = tk.Frame(root)
        gumbi.pack(pady=5)
        tk.Button(gumbi, text="Dodaj podzadatak", command=self.dodaj_podzadatak).grid(row=0, column=0, padx=5)
        tk.Button(gumbi, text="Obriši", command=self.obrisi_zadatak).grid(row=0, column=1, padx=5)
        tk.Button(gumbi, text="Spremi XML", command=self.spremi_xml).grid(row=0, column=2, padx=5)
        tk.Button(gumbi, text="Učitaj XML", command=self.ucitaj_xml).grid(row=0, column=3, padx=5)

        # --- Statusna traka ---
        self.status = tk.Label(root, text="Aktivnih: 0 | Dovršenih: 0", anchor="w")
        self.status.pack(fill="x")

        # --- Meni ---
        menubar = tk.Menu(root)
        pomoc_menu = tk.Menu(menubar, tearoff=0)
        pomoc_menu.add_command(label="O aplikaciji", command=self.o_aplikaciji)
        menubar.add_cascade(label="Pomoć", menu=pomoc_menu)
        root.config(menu=menubar)

        # --- Učitavanje i podsjetnik ---
        if os.path.exists("zadaci.xml"):
            self.ucitaj_xml()
        self.podsjetnik()

    # ==========================
    # LOGIKA
    # ==========================

    def dodaj_zadatak(self, roditelj=None):
        opis = self.opis_entry.get().strip()
        rok = self.rok_entry.get().strip()
        prioritet = self.prioritet_cb.get()
        if not opis or not rok:
            messagebox.showwarning("Upozorenje", "Unesi opis i rok!")
            return
        try:
            zad = Zadatak(opis, rok, prioritet)
        except Exception:
            messagebox.showwarning("Greška", "Rok mora biti u formatu YYYY-MM-DD!")
            return

        if roditelj:
            roditelj.dodaj_podzadatak(zad)
        else:
            self.zadaci.append(zad)

        self.osvjezi()
        self.azuriraj_status()
        self.opis_entry.delete(0, tk.END)
        self.rok_entry.delete(0, tk.END)

    def dodaj_podzadatak(self):
        selekcija = self.tree.selection()
        if not selekcija:
            messagebox.showwarning("Upozorenje", "Odaberi glavni zadatak.")
            return
        node_id = selekcija[0]
        zad = self.tree.item(node_id, "values")
        opis = simpledialog.askstring("Podzadatak", "Opis podzadatka:")
        rok = simpledialog.askstring("Podzadatak", "Rok (YYYY-MM-DD):")
        if not opis or not rok:
            return
        novi = Zadatak(opis, rok, "Srednji")
        roditelj = self.tree_to_obj[node_id]
        roditelj.dodaj_podzadatak(novi)
        self.osvjezi()
        self.azuriraj_status()

    def toggle_dovrsen(self, event=None):
        selekcija = self.tree.selection()
        if not selekcija:
            return
        node_id = selekcija[0]
        zad = self.tree_to_obj[node_id]
        zad.oznaci_dovrsen()
        self.osvjezi()
        self.azuriraj_status()

    def obrisi_zadatak(self):
        selekcija = self.tree.selection()
        if not selekcija:
            return
        node_id = selekcija[0]
        zad = self.tree_to_obj[node_id]
        if zad.roditelj:
            zad.roditelj.podzadaci.remove(zad)
        else:
            self.zadaci.remove(zad)
        self.osvjezi()
        self.azuriraj_status()

    # ==========================
    # PRIKAZ
    # ==========================

    def osvjezi(self):
        self.tree.delete(*self.tree.get_children())
        self.tree_to_obj = {}  # mapa node_id -> Zadatak
        for zad in self.zadaci:
            self.dodaj_u_tree("", zad)

    def dodaj_u_tree(self, parent, zad):
        text = f"✓ {zad.opis}" if zad.dovrsen else zad.opis
        color = self.boja_po_prioritetu(zad.prioritet)
        node = self.tree.insert(parent, "end", text=text, values=(zad.rok.strftime("%Y-%m-%d"), zad.prioritet))
        self.tree.tag_configure(zad.prioritet, background=color)
        self.tree_to_obj[node] = zad
        for pz in zad.podzadaci:
            self.dodaj_u_tree(node, pz)

    def boja_po_prioritetu(self, p):
        return {"Visok": "#ff9999", "Srednji": "#fff2cc", "Nizak": "#d9ead3"}.get(p, "#ffffff")

    # ==========================
    # SPREMANJE I UČITAVANJE XML
    # ==========================

    def spremi_xml(self):
        root = ET.Element("zadaci")

        def dodaj(el_parent, zad):
            e = ET.SubElement(el_parent, "zadatak", opis=zad.opis,
                              rok=zad.rok.strftime("%Y-%m-%d"),
                              prioritet=zad.prioritet,
                              dovrsen=str(zad.dovrsen))
            for pz in zad.podzadaci:
                dodaj(e, pz)

        for z in self.zadaci:
            dodaj(root, z)

        ET.ElementTree(root).write("zadaci.xml", encoding="utf-8", xml_declaration=True)
        messagebox.showinfo("Spremanje", "Zadaci su spremljeni!")

    def ucitaj_xml(self):
        if not os.path.exists("zadaci.xml"):
            return
        tree = ET.parse("zadaci.xml")
        root = tree.getroot()

        def ucitaj(e):
            z = Zadatak(e.attrib["opis"], e.attrib["rok"], e.attrib["prioritet"])
            z.dovrsen = e.attrib.get("dovrsen") == "True"
            for pz in e.findall("zadatak"):
                z.dodaj_podzadatak(ucitaj(pz))
            return z

        self.zadaci = [ucitaj(e) for e in root.findall("zadatak")]
        self.osvjezi()
        self.azuriraj_status()

    # ==========================
    # POMOĆNE
    # ==========================

    def azuriraj_status(self):
        svi = self.svi_zadaci()
        aktivni = len([z for z in svi if not z.dovrsen])
        dovrseni = len(svi) - aktivni
        self.status.config(text=f"Aktivnih: {aktivni} | Dovršenih: {dovrseni}")

    def svi_zadaci(self):
        def flatten(lista):
            r = []
            for z in lista:
                r.append(z)
                r.extend(flatten(z.podzadaci))
            return r
        return flatten(self.zadaci)

    def podsjetnik(self):
        danas = datetime.today().date()
        sutra = danas + timedelta(days=1)
        uskoro = [z for z in self.svi_zadaci() if z.rok.date() in (danas, sutra) and not z.dovrsen]
        if uskoro:
            tekst = "\n".join(f"- {z.opis} ({z.rok.strftime('%Y-%m-%d')})" for z in uskoro)
            messagebox.showinfo("Podsjetnik", f"Zadaci za danas/sutra:\n\n{tekst}")

    def o_aplikaciji(self):
        messagebox.showinfo("O aplikaciji", "TaskFlow Pro\nNapredna To-Do lista s XML spremanjem i podzadatcima.")


# ==========================
# POKRETANJE
# ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskFlowPro(root)
    root.mainloop()