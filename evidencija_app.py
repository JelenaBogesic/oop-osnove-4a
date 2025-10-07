import tkinter as tk
from tkinter import messagebox

class Ucenik:
    def __init__(self,ime, prezime, razred):
        self.ime=ime
        self.prezime=prezime
        self.razred=razred

    def __str__(self):
        return f"{self.ime} {self.prezime}, Razred:{(self.razred)}"
ucenik1=(Ucenik("Pero", "Perić", "4.a"))
print(ucenik1)
    

class EvidencijaApp:
    def __init__(self,root):
        self.root=root
        self.root.title("Evidencija učenika")
        self.root.geometry(500x600)

        self.ucenici=[]


        

        glavni_frame = tk.Frame(root, padx=10, pady=10)
        glavni_frame.grid(row=0, column=0, sticky="NSEW")



        self.root.columnoconfigure(0, weight=1)
        self.root.rowconfigure(0,weight=1)

        
        
        frame.columnconfigure(1, weight=1)

        
        tk.Label(frame, text="Ime:").grid(row=0, column=0, sticky="W", pady=2)
        ime_entry = tk.Entry(frame)
        ime_entry.grid(row=0, column=1, sticky="EW", pady=2) 

        tk.Label(glavni_frame, text="Email:").grid(row=1, column=0, sticky="W", pady=2)
        email_entry = tk.Entry(frame)
        email_entry.grid(row=1, column=1, sticky="EW", pady=2)

        spremi_gumb = tk.Button(frame, text="Spremi")
        spremi_gumb=spremi_gumb.grid(row=2, column=1, sticky="EW", pady=5) 


 if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()



        