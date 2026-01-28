from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
from application.core_manager import CoreManager 

class RestApiServer:
    
    def __init__(self, core_manager: CoreManager, app: Flask, host, port): # ⬅️ Solo CoreManager
        # Iniezione della Dipendenza (L'unico oggetto iniettato)
        self.core_manager = core_manager
        
        # Configurazione Host/Port/Flask
        self.host = host
        self.port = port
        self.app = app

        CORS(self.app)
        
        # Mappatura degli URL alle funzioni
        self._add_url_rules()

    def _add_url_rules(self):
        """Mappa gli endpoint REST alle funzioni handler."""
        # 1. Endpoint di Ricerca per Nome
        self.app.add_url_rule(rule='/api/tcg/search_name', endpoint='get_cards_by_name', view_func=self.handle_search_cards_by_name, methods=['GET'])
        
        # 2. Endpoint di Gestione COLLEZIONE (GET, POST e DELETE)
        self.app.add_url_rule('/api/collection', 'handle_collection', self.handle_collection, methods=['POST', 'GET', 'DELETE'])

        # 3. Endpoint ricerca per ID
        self.app.add_url_rule('/api/tcg/search_id', 'get_card_by_id', self.handle_search_card_by_id, methods=['GET']) 

    # --- HANDLERS ---

    def handle_search_cards_by_name(self):
        """Handler per GET /api/tcg/search?name=<query>"""
        name_query = request.args.get('name')
        
        if not name_query:
            return jsonify({"error": "Missing 'name' query parameter"}), 400

        try:
            
            results = self.core_manager.search_cards_by_name(name_query) 
            
            if not results:
                return jsonify({"message": f"No cards found matching '{name_query}'"}), 404
                
            return jsonify(results)
        except Exception as e:
            print(f"Errore server durante la ricerca nome: {e}")
            return jsonify({"error": "External API Error or Timeout."}), 503

    def handle_collection(self):
        """Handler per /api/collection (GET, POST, DELETE)"""
        if request.method == 'POST':
            card_data = request.json
            if not card_data or 'id' not in card_data:
                return jsonify({"error": "Invalid card data provided"}), 400
                
            
            success, message = self.core_manager.add_card_to_collection(card_data)
            
            if success:
                return jsonify({"message": message}), 201
            else:
                return jsonify({"message": message}), 409
                
        elif request.method == 'GET':
            search_query = request.args.get('name') 
            collection = self.core_manager.get_user_collection(search_query=search_query)
            return jsonify(collection)
        
        elif request.method == 'DELETE':
            card_id = request.args.get('id')
            if not card_id:
                return jsonify({"error": "Missing 'id' query parameter"}), 400
            
            # ⬅️ DELEGA: Chiama il CoreManager per eliminare
            success, message = self.core_manager.delete_card_from_collection(card_id)
            
            if success:
                return jsonify({"message": message})
            else:
                return jsonify({"message": message}), 404
    
    
    def handle_search_card_by_id(self):
        """Handler per GET /api/tcg/search?id=<card_id>"""
        card_id = request.args.get('id')
        
        if not card_id:
            return jsonify({"error": "Missing 'id' query parameter"}), 400

        try:
            # ⬅️ DELEGA: Chiama il CoreManager per la ricerca esterna
            card = self.core_manager.search_card_by_id(card_id)
            
            if not card:
                return jsonify({"message": f"No card found with ID '{card_id}'"}), 404
            
            return jsonify(card)
        except Exception as e:
            return jsonify({"error": f"Internal Server Error or PokeTCG API issue: {str(e)}"}), 503
            

    # --- METODI DI AVVIO/STOP ---

    def run_server(self):
        """Metodo per avviare il server (target per il thread)."""
        self.app.run(host=self.host, port=self.port, debug=True, use_reloader=False)

    def start(self):
        """Avvia il server in un thread separato (opzionale, ma pulito)."""
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()
        print(f"REST API Server running on http://{self.host}:{self.port}")