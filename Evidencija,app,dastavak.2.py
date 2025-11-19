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








    ✅ KREĆEMO — BLOK 1: UVOZI MODULA
1. dio
import tkinter as tk


➡️ Uvozi Python biblioteku tkinter, koja služi za izradu grafičkih prozora i sučelja.
➡️ Daje joj kraće ime tk, da se lakše piše.
🔸 Za aplikaciju: omogućuje stvaranje prozora, gumba, tekstualnih polja itd.

from tkinter import ttk, messagebox, simpledialog


➡️ Uvozi dodatne alate iz tkintera:

ttk – moderniji izgled kontrola (treeview, combobox…)

messagebox – iskakanje poruka (upozorenja, informacije)

simpledialog – mali prozori koji traže unos teksta
🔸 Za aplikaciju: koristiš ih za prikaz upozorenja, unos podzadataka, i prikaz stablastog popisa.

import xml.etree.ElementTree as ET


➡️ Uvozi alat za rad s XML datotekama.
➡️ Omogućuje čitanje i pisanje struktura u XML formatu.
🔸 Za aplikaciju: omogućuje pohranu zadataka i kasnije učitavanje.

from datetime import datetime, timedelta


➡️ Uvozi objekte za rad s datumima.

datetime – točan datum

timedelta – razlika između datuma
🔸 Za aplikaciju: izračun roka, usporedba datuma za podsjetnike, zapisivanje roka.

import os


➡️ Uvozi modul za rad s datotekama i provjeru postoji li neka datoteka.
🔸 Za aplikaciju: provjerava postoji li zadaci.xml pri pokretanju.

BLOK 2 — DEFINICIJA MODELA (Zadatak)
class Zadatak:


➡️ Stvara "kalup" (klasu) za svaki zadatak.
🔸 Za aplikaciju: ovo je način da svaki zadatak ima opis, rok, prioritet, podzadatke itd.

    def __init__(self, opis, rok, prioritet="Srednji", roditelj=None):


➡️ Ovo je funkcija koja se pokreće kad god se napravi novi zadatak.
➡️ Prima podatke: opis, rok, prioritet i opcionalno roditelj (ako je podzadatak).
🔸 Za aplikaciju: svaki zadatak odmah dobiva sve potrebne podatke.

        self.opis = opis


➡️ Sprema tekst zadatka.

        self.rok = datetime.strptime(rok, "%Y-%m-%d") if isinstance(rok, str) else rok


➡️ Ako je rok zapisan kao tekst (npr. "2025-01-20"), pretvara ga u pravi datum.
➡️ Ako je već datum, ostavlja ga tako.
🔸 Za aplikaciju: omogućuje rad s datumima i usporedbu.

        self.prioritet = prioritet


➡️ Sprema prioritet (Visok, Srednji, Nizak).

        self.roditelj = roditelj


➡️ Pamti kojem zadatku ovaj pripada (ako je podzadatak).

        self.podzadaci = []


➡️ Stvara praznu listu u koju idu podzadaci.

        self.dovrsen = False


➡️ Bilježi je li zadatak završeno ili ne.

Metoda: označavanje dovršeno / nedovršeno
    def oznaci_dovrsen(self, stanje=None):


➡️ Funkcija koja označuje zadatak kao gotov ili nedovršen.
🔸 Za aplikaciju: klikom na zadatak dvaput, mijenja njegovo stanje.

        if stanje is None:
            self.dovrsen = not self.dovrsen


➡️ Ako nije zadano stanje, prebacuje ga suprotno (True → False i obrnuto).

        else:
            self.dovrsen = stanje


➡️ Ako ima stanje, postavlja ga izravno.

        for pz in self.podzadaci:
            pz.oznaci_dovrsen(self.dovrsen)


➡️ Ako je glavni zadatak označen kao dovršen, automatski dovršava i sve podzadatke.

Dodavanje podzadatka
    def dodaj_podzadatak(self, podzadatak):


➡️ Funkcija za dodavanje podzadatka.

        self.podzadaci.append(podzadatak)


➡️ Podzadatak se dodaje u listu.

        podzadatak.roditelj = self


➡️ Postavlja roditelja na trenutni zadatak.

BLOK 3 — GRAFIČKA APLIKACIJA (TaskFlowPro)
class TaskFlowPro:


➡️ Glavna klasa aplikacije – sve što korisnik vidi i što se događa vodi ova klasa.

    def __init__(self, root):


➡️ Početna funkcija — pokreće se kada se aplikacija otvori.
🔸 Za aplikaciju: gradi sve gumbe, polja, meni, učitava zadatke itd.

        self.root = root


➡️ Sprema glavni prozor.

        self.root.title("TaskFlow Pro – Upravljanje zadacima")


➡️ Postavlja naslov prozora.

        self.zadaci = []


➡️ Prazna lista u koju idu glavni zadaci (bez roditelja).

✔️ Gornji okvir (unos zadataka)
        frame = tk.Frame(root)
        frame.pack(pady=10)


➡️ Stvara okvir (grupni blok) gdje se nalaze polja za unos zadataka.
➡️ Dodaje malo razmaka gore-dolje.

        tk.Label(frame, text="Opis:").grid(row=0, column=0, padx=5)


➡️ Tekst "Opis:" na lijevoj strani.

        self.opis_entry = tk.Entry(frame, width=30)
        self.opis_entry.grid(row=0, column=1)


➡️ Polje gdje korisnik upiše naziv zadatka.

        tk.Label(frame, text="Rok (YYYY-MM-DD):").grid(row=1, column=0)
        self.rok_entry = tk.Entry(frame, width=30)
        self.rok_entry.grid(row=1, column=1)


➡️ Polje za unos roka zadatka.

        tk.Label(frame, text="Prioritet:").grid(row=2, column=0)


➡️ Tekst "Prioritet".

        self.prioritet_cb = ttk.Combobox(frame, values=["Visok", "Srednji", "Nizak"], state="readonly", width=27)


➡️ Padajući izbornik za odabir prioriteta.

        self.prioritet_cb.set("Srednji")


➡️ Zadaje početnu vrijednost: Srednji.

        self.prioritet_cb.grid(row=2, column=1)


➡️ Postavlja ga na odgovarajuće mjesto u mreži.

        tk.Button(frame, text="Dodaj zadatak", command=self.dodaj_zadatak).grid(row=3, column=0, columnspan=2, pady=5)


➡️ Gumb "Dodaj zadatak".
➡️ Kada se klikne → pokreće self.dodaj_zadatak.

BLOK 4 — TREEVIEW (stablo zadataka)
        self.tree = ttk.Treeview(root, columns=("rok", "prioritet"), show="tree headings")


➡️ Stvara stablo gdje se zadaci prikazuju hijerarhijski (zadatak → podzadatak).
➡️ Dodatne kolone: rok i prioritet.

        self.tree.heading("#0", text="Zadatak")
        self.tree.heading("rok", text="Rok")
        self.tree.heading("prioritet", text="Prioritet")


➡️ Nazivi stupaca u tablici.

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)


➡️ Prikazuje stablo i širi ga preko cijelog prozora.

        self.tree.bind("<Double-Button-1>", self.toggle_dovrsen)


➡️ Ako korisnik dvaput klikne zadatak → označit će se kao dovršen/nedovršen.

BLOK 5 — Gumbi ispod stabla
        gumbi = tk.Frame(root)
        gumbi.pack(pady=5)


➡️ Okvir za grupiranje gumba.

        tk.Button(gumbi, text="Dodaj podzadatak", command=self.dodaj_podzadatak).grid(row=0, column=0, padx=5)


➡️ Gumb za dodavanje podzadatka.

        tk.Button(gumbi, text="Obriši", command=self.obrisi_zadatak).grid(row=0, column=1, padx=5)


➡️ Gumb za brisanje odabranog zadatka.

        tk.Button(gumbi, text="Spremi XML", command=self.spremi_xml).grid(row=0, column=2, padx=5)
        tk.Button(gumbi, text="Učitaj XML", command=self.ucitaj_xml).grid(row=0, column=3, padx=5)


➡️ Dva gumba za spremanje i učitavanje XML datoteka.

BLOK 6 — Statusna traka
        self.status = tk.Label(root, text="Aktivnih: 0 | Dovršenih: 0", anchor="w")
        self.status.pack(fill="x")


➡️ Traka na dnu koja prikazuje broj aktivnih i dovršenih zadataka.

BLOK 7 — Meni
        menubar = tk.Menu(root)
        pomoc_menu = tk.Menu(menubar, tearoff=0)


➡️ Stvara gornji meni.

        pomoc_menu.add_command(label="O aplikaciji", command=self.o_aplikaciji)


➡️ Dodaje stavku "O aplikaciji".

        menubar.add_cascade(label="Pomoć", menu=pomoc_menu)
        root.config(menu=menubar)


➡️ Stavlja meni u prozor.

BLOK 8 — Učitavanje pri pokretanju
        if os.path.exists("zadaci.xml"):
            self.ucitaj_xml()


➡️ Ako datoteka postoji → automatski učitava.

        self.podsjetnik()


➡️ Prikazuje obavijesti za zadatke koji istječu danas ili sutra.

❗ Želiš li da nastavim OBJAŠNJAVANJE SVIH FUNKCIJA (dodaj_zadatak, dodaj_podzadatak, spremi_xml itd.) ISTIM DETALJNIM STILOM?

Kod je jako dug, pa ću nastaviti tek kad potvrdiš da želiš ovako detaljno dalje.