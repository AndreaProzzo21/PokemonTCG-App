from flask import Flask
from sqlalchemy.exc import IntegrityError
from persistence.database.model import db, Card, Set 
from sqlalchemy import select
from sqlalchemy import func

class DataManager:
    """
    Gestisce le operazioni CRUD (Create, Read, Update, Delete)
    sulla collezione di carte utilizzando SQLite/SQLAlchemy.
    """
    
    def __init__(self, app: Flask):
        # Il DataManager ha bisogno dell'istanza Flask per eseguire operazioni sul DB
        self.app = app
        
    
    def _get_or_create_set(self, set_id: str, set_name: str):
        """
        Funzione helper: Cerca un Set per ID. Se non esiste, lo crea per la Foreign Key.
        """
        # Tutte le query interne devono essere nel contesto. Assumiamo che la funzione chiamante lo faccia.
        
        # 1. Cerca il Set
        set_obj = db.session.get(Set, set_id) 
        
        if set_obj is None:
            # 2. Se non trovato, crea un nuovo Set con dati di base
            set_obj = Set(id=set_id, name=set_name, release_date="N/A") 
            db.session.add(set_obj)
            # Il commit avverrà solo se la Card viene salvata con successo.
        return set_obj

    def add_card(self, card_data: dict):
        """
        Aggiunge una nuova carta al database, gestendo la relazione Set.
        """
        # Tutte le operazioni DB devono avvenire nel contesto dell'app
        with self.app.app_context():
            try:
                card_id = card_data.get('id')
                
                # 1. Validazione e Controllo Duplicati (Query sul DB)
                if db.session.get(Card, card_id):
                    return False, f"Card ID {card_id} is already in the collection."
                
                # 2. Gestione del Set (Foreign Key): I campi vengono passati dal CoreManager/DTO
                # I campi vengono passati puliti grazie al Fetcher/DTO:
                set_id = card_data.get('set_id') 
                set_name = card_data.get('set_name')   
                
                if not set_id:
                     # Questo dovrebbe essere catturato dal CoreManager, ma qui facciamo un controllo finale
                     return False, "Missing Set ID required for database integrity."

                set_obj = self._get_or_create_set(set_id, set_name)
                
                # 3. Creazione dell'oggetto Card
                new_card = Card(
                    id=card_id,
                    name=card_data.get('name', 'Unknown Card'),
                    type=card_data.get('type'),
                    rarity=card_data.get('rarity'),
                    image_url=card_data.get('image_url'),
                    # Collega l'oggetto Set tramite la relazione
                    set_info=set_obj 
                )
                
                db.session.add(new_card)
                db.session.commit()
                
                return True, f"Card {card_data.get('name')} successfully added to collection."
                
            except IntegrityError:
                db.session.rollback()
                return False, "Database error (Integrity constraint failed). Annullamento transazione."
            except Exception as e:
                db.session.rollback()
                return False, f"Unexpected DB Error: {e}"

    # --- READ (Tutti) ---
    def get_all_card(self, search_query: str = None) -> list:
    
        with self.app.app_context():
        # Inizia la query di selezione
            stmt = db.select(Card).order_by(Card.name.asc())
        
        # LOGICA CRITICA: Applica il filtro SOLO se la query è presente
            if search_query:
                # Filtra i risultati se la query è fornita
                stmt = stmt.where(func.lower(Card.name).like(f'%{search_query.lower()}%'))
        
            # Esegue la query aggiornata (filtrata o completa)
            cards = db.session.execute(stmt).scalars().all()
            
            # Mappa gli oggetti SQLAlchemy in una lista di dizionari JSON-serializzabili
            return [
                {
                    'id': card.id,
                    'name': card.name,
                    'type': card.type,
                    'rarity': card.rarity,
                    'image_url': card.image_url,
                    # Accesso alla relazione per recuperare il nome del set
                    'set': card.set_info.name if card.set_info else 'Unknown Set', 
                    'set_id': card.set_id
                } 
                for card in cards
            ]

    # --- READ (Singolo) ---
    def get_card_by_id(self, card_id: str):
        """Recupera i dettagli di una singola carta tramite ID."""
        with self.app.app_context():
            card = db.session.get(Card, card_id)
            if card:
                return {
                    'id': card.id,
                    'name': card.name,
                    'type': card.type,
                    'rarity': card.rarity,
                    'image_url': card.image_url,
                    'set': card.set_info.name if card.set_info else 'Unknown Set',
                    'set_id': card.set_id
                }
            return None # Restituisce None se non trovata

    # --- DELETE ---
    def delete_card_by_id(self, card_id: str):
        """Rimuove una carta dal database."""
        with self.app.app_context():
            card_to_delete = db.session.get(Card, card_id)
            if card_to_delete:
                db.session.delete(card_to_delete)
                db.session.commit()
                # ⬅️ Logica di debug (rimossa la stampa diretta dal return)
                return True, f"Card ID {card_id} deleted."
            
            print(f"[DM DELETE] Carta non trovata ID: {card_id}")
            return False, f"Card ID {card_id} not found."