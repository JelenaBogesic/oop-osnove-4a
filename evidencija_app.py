
import tkinter as tk
import csv
class Ucenik:
    def __init__(self, ime, prezime, razred):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self):
        return f"UÄŤenik: {self.ime} {self.prezime} iz razreda {self.razred}"
    

class EvidencijaApp:
    def __init__(self, root):
        self.ucenici = []
        self.odabrani_ucenik_index = None

        root.title("Evidencija uÄŤenika")
        root.geometry("500x400")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        unos_frame = tk.Frame(root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW")

        prikaz_frame = tk.Frame(root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW")

        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)

        tk.Label(unos_frame, text="Ime:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, padx=30, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Prezime:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.prezime_entry = tk.Entry(unos_frame)
        self.prezime_entry.grid(row=1, column=1, padx=30, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Razred:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.razred_entry = tk.Entry(unos_frame)
        self.razred_entry.grid(row=2, column=1, padx=30, pady=5, sticky="EW")

        dodaj_gumb = tk.Button(unos_frame, text="Dodaj učenika", command=self.dodaj_ucenika)
        dodaj_gumb.grid(row=3, column=0, padx=5, pady=10, sticky="W")

        spremi_gumb = tk.Button(unos_frame, text="Spremi izmjene", width=35, command=self.spremi_izmjene)
        spremi_gumb.grid(row=3, column=1, padx=30, pady=10, sticky="E")

        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")
        self.listbox.bind("<<ListboxSelect>>", self.odaberi_ucenika)

        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

    def dodaj_ucenika(self):
        ime = self.ime_entry.get()
        prezime = self.prezime_entry.get()
        razred = self.razred_entry.get()

        if ime and prezime and razred:
            ucenik = Ucenik(ime, prezime, razred)
            self.ucenici.append(ucenik)
            self.osvjezi_prikaz()

            self.ime_entry.delete(0, tk.END)
            self.prezime_entry.delete(0, tk.END)
            self.razred_entry.delete(0, tk.END)

    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)

        for ucenik in self.ucenici:
            self.listbox.insert(tk.END, str(ucenik))

    def odaberi_ucenika(self, event):
        selected_index = self.listbox.curselection()

        if selected_index:
            self.odabrani_ucenik_index = selected_index[0]
            ucenik = self.ucenici[self.odabrani_ucenik_index]

            self.ime_entry.delete(0, tk.END)
            self.ime_entry.insert(0, ucenik.ime)
            self.prezime_entry.delete(0, tk.END)
            self.prezime_entry.insert(0, ucenik.prezime)
            self.razred_entry.delete(0, tk.END)
            self.razred_entry.insert(0, ucenik.razred)

    def spremi_izmjene(self):
        if self.odabrani_ucenik_index is not None:
            ucenik = self.ucenici[self.odabrani_ucenik_index]

            ucenik.ime = self.ime_entry.get()
            ucenik.prezime = self.prezime_entry.get()
            ucenik.razred = self.razred_entry.get()

            self.osvjezi_prikaz()

            self.ime_entry.delete(0, tk.END)
            self.prezime_entry.delete(0, tk.END)
            self.razred_entry.delete(0, tk.END)

            self.odabrani_ucenik_index = None


     def spremi_ucenike_csv( filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            polja = ['Ime', 'Prezime', 'Razred']
            writer = csv.DictWriter(file, fieldnames=polja)
            writer.writeheader()
            for ucenik in lista_ucenika:
                writer.writerow({'Ime': ucenik.ime, 'Prezime': ucenik.prezime, 'Razred': ucenik.razred})
        print(f"Učenici su spremljeni u {filename}")
    
    def ucitaj_ucenike_csv(filename):
        ucitani_ucenici = []
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for red in reader:
                ucenik = Ucenik(red['Ime'], red['Prezime'], red['Razred'])
                ucitani_ucenici.append(ucenik)
            print(f"Učenici su učitani iz {filename}")
            return ucitani_ucenici
                



        

if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()


                



        