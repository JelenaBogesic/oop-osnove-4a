class BankovniRacun:
    """klasa koja modelira jednostavni bankovni račun."""
    def _init_(self, ime_prezime, broj_racuna):
        """konstruktor za BankovniRčun"""
        self.ime_prezime=ime_prezime
        self.broj_racuna= broj_racuna
        self.stanje= 0.0

    def uplati (self, iznos):
        """Metoda za uplatu novca na fračun."""
        if iznos>0:
            self.stanje+=iznos
            print(f"Uplata od {iznos:.2f} EUR na račun {self.broj_racuna}je uspješna.")
        else:
            print("neispravan iznos za uplatu. Iznos mora biti pozitivan")

    def isplati(self, iznos):
        if iznos<=0:
            print("Greška iznos za isplatu mora biti pozitivan.")
        elif self.stanje>= iznos:
            self.stanje -= iznos
            print (f"Isplata od {iznos: .2f} EUR uspješna Novo stanje:{self.stanje: .2f}EUR.")
        else:
            print(f"Isplata nije moguća. Nedovoljno sredstva(Stanje:{self.stanje: .2f}EUR)")


    def info(self):
        print(f"Vlasnik računa:{self.ime_prezime}")
        print(f"Broj računa: {self.broj_racuna}")
        print(f"Stanje sašuna: {self.stanje:.2f}")
racun1=BankovniRacun("Mathias ćus", "HR12334457")
racun1.info()
racun1.uplati(1000)
racun1.isplati(200)
racun1.info()
print("/n" + "="*30 + "/n")
