from persistence.data_manager import DataManager 
from communication.api.tcg_fetcher import TCGFetcher 

class CoreManager:
    """
    Core Manager: Agisce come ponte tra il Livello API/Web e i Livelli di Persistenza e Comunicazione Esterna.
    Orchestra l'arricchimento dei dati (ID Lookup) solo al momento del salvataggio.
    """
    
    def __init__(self, data_manager: DataManager, tcg_fetcher: TCGFetcher):
        self.data_manager = data_manager
        self.tcg_fetcher = tcg_fetcher
        self.api_call_counter = 0
        

    # -------------------------------------------------------------------
    # METODI PER LA RICERCA ESTERNA (Proxy Semplice)
    # -------------------------------------------------------------------

    def search_cards_by_name(self, name_query: str) -> list:
        """
        Passa la richiesta di ricerca al TCGFetcher. Non esegue l'arricchimento.
        Restituisce i dati brevi per la visualizzazione nel frontend.
        """
        self.api_call_counter += 1
        print(f"[CORE MONITOR] Richiesta API N° {self.api_call_counter} (Ricerca per nome) in corso...")
        
        if not name_query:
            return []
    
        try:
            # Chiama il Fetcher (restituisce lista di dizionari DTO-compatibili con N/A)
            simplified_cards = self.tcg_fetcher.search_cards_by_name(name_query)
            print(f"[CoreManager] Trovate {len(simplified_cards)} carte. Visualizzazione breve.")
        except Exception as e:
            print(f"Errore nella Fase di ricerca breve: {e}")
            return []
            
        return simplified_cards
    
    def search_card_by_id(self, card_id: str) -> dict:
        """
        Passa la richiesta di ricerca per ID al TCGFetcher.
        """
        self.api_call_counter += 1 
        print(f"[CORE MONITOR] Richiesta API N° {self.api_call_counter} (Ricerca ID) in corso...")
        
        if not card_id:
            return {}

        return self.tcg_fetcher.search_card_by_id(card_id)

    # -------------------------------------------------------------------
    # METODI PER LA COLLEZIONE INTERNA (Ponte con DataManager)
    # -------------------------------------------------------------------

    def add_card_to_collection(self, card_data_brief: dict):
        """
        Orchestra il processo di salvataggio: esegue l'ID Lookup (Arricchimento) e poi salva.
        """
        card_id = card_data_brief.get('id')
        
        if not card_id or card_id == 'N/A':
            return False, "ID della carta mancante o non valido per il salvataggio."

        # 1. ESEGUIRE L'ID LOOKUP PER OTTENERE I DATI COMPLETI (Arricchimento)
        print(f"[CORE MANAGER] Esecuzione Lookup ID per arricchimento: {card_id}...")
        
        # Chiama la funzione di lookup ID
        full_card_data = self.search_card_by_id(card_id)
        #print(full_card_data)
        
        if not full_card_data or full_card_data.get('id') != card_id:
            return False, f"Impossibile trovare dati completi per la carta ID: {card_id}."
        
        # Verifica cruciale per il Set
        set_name = full_card_data.get('set')
        set_id = full_card_data.get('set_id')
        
    
        # Costruiamo il payload per il DataManager
        payload_to_save = {
            **full_card_data, 
            'set_id': set_id, 
            'set_name': set_name
        }

        # Se set_id è None o N/A dopo l'arricchimento, blocca il salvataggio qui
        if not payload_to_save.get('set_id') or payload_to_save.get('set_id') == 'N/A':
            return False, "Dati incompleti: ID del Set mancante dopo l'arricchimento."

        # 2. Passa i dati COMPLETI (arricchiti) al DataManager
        return self.data_manager.add_card(payload_to_save) # Il DM deve ricevere set_id e set_name

    def get_user_collection(self, search_query):
        """Recupera la collezione dell'utente dal DataManager."""
        print(f"[CORE -> DM] Ricevuta richiesta GET per collezione")
        return self.data_manager.get_all_card(search_query)
        
    def delete_card_from_collection(self, card_id: str) -> tuple:
        """Elimina una carta tramite ID."""
        print(f"[CORE -> DM] Ricevuta richiesta DELETE per cancellare ID: {card_id}")
        return self.data_manager.delete_card_by_id(card_id)