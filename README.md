# Pokémon TCG Collection Tracker

A full-stack web application designed to browse, search, and manage a personal Pokémon Trading Card Game collection. Built with Python (Flask) and JavaScript.

### Project Architecture

The project follows a **Layered Architecture**:

1. **Persistence Layer (`DataManager` + SQLAlchemy):** Handles the SQLite database. It manages the `Card` and `Set` models, ensuring data integrity and handling local searches/filtering.
2. **Communication Layer (`TCGFetcher`):** The external gateway. It talks to the TCGDEX API and converts raw JSON into clean **DTOs (Data Transfer Objects)**.
3. **Application Layer (`CoreManager`):** The "brain." It orchestrates logic between the API and the Database. It performs **Data Enrichment**: when you save a card, it automatically fetches the "Full Details" from the API before committing to the DB.
4. **Interface Layer (`RestApiServer` + Frontend):** A Flask REST API that serves data to a modern, responsive JS frontend.

## 🚀 Features

* **Global Card Search:** Search for any card by name or specific ID using the TCGDEX API.
* **Data Enrichment:** Automatically fetches high-resolution images, rarity, and set details when adding a card to your collection.
* **Local Collection Management:** Save your favorite cards to a local SQLite database.
* **Smart Filtering:** Search and filter through your personal collection locally.
* **Responsive Dashboard:** A clean, modern UI with tabbed navigation and real-time status updates.

## 🏗️ Architecture

The project is built using a layered architectural pattern to ensure maintainability:

* **Frontend:** HTML5, CSS, and JavaScript (Asynchronous Fetch API).
* **Backend:** Flask (Python) with a Threaded REST Server.
* **Core Logic:** A Centralized Manager that orchestrates data flow between external APIs and internal storage.
* **Database:** SQLAlchemy ORM with SQLite for persistent storage of cards and sets.
* **API Integration:** Connects to the TCGDEX API (No API Key required).

## 🛠️ Installation

1. **Clone the repository**
```bash
   git clone [https://github.com/yourusername/PokemonTCG-App.git](https://github.com/yourusername/PokemonTCG-App.git)
   cd PokemonTCG-App

```


2. **Install Dependencies**
```bash
   pip install flask flask-cors flask-sqlalchemy pyyaml requests

```


3. **Configuration**
Ensure you have a `config.yaml` in the root directory with the following structure:
```yaml
api:
  base_url: "[https://api.tcgdex.net/v2](https://api.tcgdex.net/v2)"
  cards_endpoint: "/en/cards"

```


4. **Run the Application**
Run your main entry point script:
```bash
python main.py

```


The server will start on `http://localhost:5000`. Open `index.html` in your browser to start tracking!

## 📂 Project Structure

* `communication/` - API Fetcher and DTO definitions.
* `persistence/` - Database models and CRUD logic (DataManager).
* `application/` - CoreManager for business logic orchestration.
* `api/` - Flask REST Server implementation.
* `presentation/` - Frontend files (HTML, CSS, JS).

## 🤝 Contributing & Suggestions

This project is open-source and constantly evolving! I built this as a foundation for Pokémon TCG fans, but there is always room for improvement.

Feel free to:
* **Open an Issue:** If you find a bug or have a suggestion for a new feature.
* **Submit a Pull Request:** If you want to contribute directly to the code (e.g., UI improvements, new API integrations, or performance optimizations).
* **Suggest Adjustments:** Whether it's about the architecture or the user experience, all feedback is welcome!

## 📝 License

This project is for educational purposes. Pokémon is a trademark of Nintendo. Data provided by TCGDEX API.


