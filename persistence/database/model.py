from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey

# 1. Istanza del Database
# Questo oggetto 'db' verrà inizializzato e collegato all'app Flask in main.py
db = SQLAlchemy()

# -------------------------------------------------------------------
# 2. TABELLA SET (Metadati sull'Espansione)
# -------------------------------------------------------------------

class Set(db.Model):
    # Nome della tabella nel database SQLite
    __tablename__ = 'set' 
    
    # Colonna che funge da Primary Key (chiave primaria)
    id = Column(String(20), primary_key=True) 
    
    # Colonne per i dettagli del Set
    name = Column(String(100), nullable=False)
    release_date = Column(String(20))
    
    # RELAZIONE: 'cards' è un attributo Python che conterrà una lista di oggetti Card 
    # che appartengono a questo Set. Il back_populates collega Card.set_info a Set.cards
    cards = relationship("Card", back_populates="set_info", lazy='dynamic')

    def __repr__(self):
        return f"<Set(id='{self.id}', name='{self.name}')>"

# -------------------------------------------------------------------
# 3. TABELLA CARD (La Tua Collezione)
# -------------------------------------------------------------------

class Card(db.Model):
    __tablename__ = 'card'

    # ID della carta TCGDEX (es. 'swsh1-1') - Primary Key
    id = Column(String(50), primary_key=True)
    
    # Dettagli della carta
    name = Column(String(150), nullable=False)
    type = Column(String(50))
    rarity = Column(String(50))
    image_url = Column(String(255))
    
    # CHIAVE ESTERNA (Foreign Key): collega la carta alla tabella 'set'
    # 'set.id' indica che si riferisce alla colonna 'id' della tabella 'set'
    set_id = Column(String(20), ForeignKey('set.id'), nullable=False)
    
    
    # RELAZIONE: 'set_info' è un attributo Python che conterrà l'oggetto Set completo 
    # a cui è collegata la carta (ti permette di accedere a card.set_info.name)
    set_info = relationship("Set", back_populates="cards")
    
    def __repr__(self):
        return f"<Card(id='{self.id}', name='{self.name}', set_id='{self.set_id}')>"

# -------------------------------------------------------------------
# 4. Funzione di inizializzazione (Da usare in main.py)
# -------------------------------------------------------------------

def initialize_db(app):
    """
    Collega l'istanza db all'app Flask e crea le tabelle.
    """
    with app.app_context():
        # Collega l'oggetto db all'app Flask
        db.init_app(app)
        # Crea le tabelle nel database se non esistono
        db.create_all()