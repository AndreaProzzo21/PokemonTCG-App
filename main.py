from persistence.data_manager import DataManager
from persistence.database.model import initialize_db, db
from communication.api.tcg_fetcher import TCGFetcher
from application.core_manager import CoreManager 
from communication.api_server import RestApiServer
from flask import Flask


TCG_CONFIG_FILE = "C:\\Users\\Admin\\PythonProjects\\DIoTSA\\PokeAPIApp_v2\\config\\api_config.yaml"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collezione.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == '__main__':
    print("--- Avvio Applicazione Mini-Pokedex TCG ---")

    initialize_db(app) 
    print("✓ Database SQLite inizializzato e tabelle create.")

    # 1. Inizializzazione dei Livelli Inferiori (Dipendenze)
    data_manager = DataManager(app=app)
    tcg_fetcher = TCGFetcher(TCG_CONFIG_FILE)

    # 2. Creazione del CORE MANAGER (L'Orchestratore)
    # Il Core Manager prende le dipendenze di Livello Dati e Livello API Esterna.
    core_manager = CoreManager(
        data_manager=data_manager, 
        tcg_fetcher=tcg_fetcher
    )
    print("✓ CoreManager (Livello Applicativo/Logico) inizializzato.")
    
    # 3. Inizializzazione e Avvio del Server REST API (Livello di Interfaccia)
    # Il server riceve SOLO il CoreManager, rendendolo disaccoppiato.
    rest_api_server = RestApiServer(
        core_manager=core_manager, 
        host='0.0.0.0', 
        port=5000,
        app=app
    )
    print("✓ RestApiServer (Livello API) inizializzato.")

    # 4. Avvio del Server
    rest_api_server.start()
    
    print(f"Applicazione avviata. Accesso REST API su http://localhost:{5000}")