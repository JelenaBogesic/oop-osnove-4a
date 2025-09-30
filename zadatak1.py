class knjiga:
    """klasa koja modelira knjigu s osnovnim podacima"""
    def __init__(self,naslov,autor,godina_izdanja):
        """Konstruktor za klau knjiga"""
        self.naslov=naslov
        self.autor= autor 
        self.godina_izdanja=godina_izdanja

knjiga1=knjiga("Hamlet"," William Shakespeare",1603)
knjiga2=knjiga("Gospodar muha","J.R.R. Tolkien",1954)
print(f"Naslov:{knjiga1.naslov},autor:{knjiga1.autor}, godina izdanja: {knjiga1.godina_izdanja}")
print(f"Naslov:{knjiga2.naslov}, autor:{knjiga2.autor}, godina izdanja:{knjiga2.godina_izdasnja}")