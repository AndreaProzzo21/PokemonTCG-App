import requests
import yaml
import os
import time
import urllib.parse
from communication.dto.card_dto import CardDTO 

class TCGFetcher:
    """
    Gestisce la comunicazione con l'API esterna TCGDEX.
    Centralizza l'estrazione dati e la conversione nel Card DTO.
    """

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self._load_config()
        
        
        self.base_url = self.config['api']['base_url']
        self.cards_endpoint = self.config['api']['cards_endpoint']
        


    def _load_config(self):
        """Carica la configurazione dal file YAML."""
        main_app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(main_app_path, self.config_file)
        
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def _create_dto_from_raw(self, card_data: dict, is_full_detail: bool) -> CardDTO:
        """
        Crea un DTO card a partire dal JSON grezzo dell'API, 
       
        """
        
        # --- 1. Campi Base e Immagine (Sempre o Placeholder) ---
        card_id = card_data.get('id', 'N/A')
        card_name = card_data.get('name', 'Unknown Card')
        
        # Gestione dell'apostrofo 
        if isinstance(card_name, str) and "'" in card_name:
            card_name = card_name.replace("'", "^")
        
        # Costruzione URL Immagine
        base_image_url = card_data.get('image', '')
        if base_image_url:
             # Aggiunge l'estensione finale (es. /high.webp)
            image_url = f"{base_image_url}/high.webp"
        else:
            image_url = "placeholder.png"

        
        # --- 2. Campi Dettagliati (Solo se la risposta è COMPLETA) ---
        
        # Se i dati sono completi (ricerca ID), li estraiamo.
        if is_full_detail:
            
            # Estrazione sicura del tipo
            types_list = card_data.get('types', [])
            main_type = types_list[0] if types_list and isinstance(types_list, list) and len(types_list) > 0 else 'Unknown'
            
            # Estrazione sicura dei dati del set
            set_obj = card_data.get('set', {})
            set_id = set_obj.get('id', 'N/A')
            set_name = set_obj.get('name', 'Unknown Set')
            rarity = card_data.get('rarity', 'N/A')

            return CardDTO(
                id=card_id,
                name=card_name,
                image_url=image_url,
                set_name=set_name,
                set_id=set_id,
                type=main_type,
                rarity=rarity
            )
        
        # 3. Caso di Risposta BREVE (Ricerca per Nome)
        else:
            # Restituisce solo i campi base. Gli altri saranno 'N/A' (default DTO).
            return CardDTO(
                id=card_id,
                name=card_name,
                image_url=image_url
            )


    def search_cards_by_name(self, name_query: str) -> list:

        if not name_query:
            return []
            
        encoded_name = urllib.parse.quote(name_query) 

        full_url_with_query = (
            f"{self.base_url}{self.cards_endpoint}"
            f"?name={encoded_name}"
        )
        
        try:
            start_time = time.time()
            response = requests.get(full_url_with_query, timeout=15) 
            response_time = time.time() - start_time
            print(f"[DEBUG FETCH NAME] API Response Time: {response_time:.2f} seconds")

            response.raise_for_status() 
        
            start_parsing_time = time.time()
            raw_cards = response.json() 
            parsing_time = time.time() - start_parsing_time
            print(f"[DEBUG FETCH NAME] JSON Parsing Time: {parsing_time:.2f} seconds")

            if not raw_cards:
                return []
            
            start_extraction_time = time.time()
            simplified_dtos = [self._create_dto_from_raw(card, is_full_detail=False) for card in raw_cards]
            extraction_time = time.time() - start_extraction_time
            print(f"[DEBUG FETCH NAME] Data Extraction Time: {extraction_time:.2f} seconds")
            
            # ⬅️ CORREZIONE 2: Restituisce una lista di dizionari per la serializzazione JSON di Flask
            return [dto.to_dict() for dto in simplified_dtos] 
            
        except requests.exceptions.RequestException as e:
            print(f"[ERRORE FATALE] Error fetching data from TCGDEX API: {e}")
            return []
    

    def search_card_by_id(self, card_id: str) -> dict:

        if not card_id:
            return {}
        
        full_url = f"{self.base_url}{self.cards_endpoint}/{card_id}"
        
        try:
            start_time = time.time()
            response = requests.get(full_url, timeout=10)
            request_duration = time.time() - start_time
            print(f"[DEBUG FETCH ID] API Respone Time: {request_duration:.4f} seconds.")
            
            response.raise_for_status() 

            start_parsing_time = time.time()
            raw_card = response.json()
            parsing_duration = time.time() - start_parsing_time
            print(f"[DEBUG FETCH ID] JSON Parsing Time: {parsing_duration:.4f} seconds.")
            
            if not raw_card or 'id' not in raw_card:
                return {}

            start_simplify_time = time.time()
            simplified_dto = self._create_dto_from_raw(raw_card, is_full_detail=True)
            simplify_duration = time.time() - start_simplify_time
            print(f"[DEBUG FETCH ID] Data Extraction time: {simplify_duration:.4f} seconds.")
            return simplified_dto.to_dict()
            
        except requests.exceptions.RequestException as e:
            print(f"[ERRORE FATALE] Errore durante il fetching dei dati per ID {card_id}: {e}")
            return {}