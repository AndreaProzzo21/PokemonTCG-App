const API_BASE_URL = 'http://localhost:5000/api';

// ------------------------------------------------------------------
// UTILITY: Gestione Stato e Rendering
// ------------------------------------------------------------------

function setStatus(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.style.backgroundColor = isError ? '#ffe0e0' : '#e0fff4';
}

/**
 * Funzione generica per eseguire tutte le richieste GET API.
 */
async function fetchData(endpoint) {
    const fullUrl = `${API_BASE_URL}/${endpoint}`;
    
    try {
        const response = await fetch(fullUrl);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.message || `Errore HTTP ${response.status}`);
        }
        return data;

    } catch (error) {
        throw new Error(`Errore di connessione: ${error.message}. Verifica console.`);
    }
}

function renderCard(card, isCollection = false) {
    const cardHtml = document.createElement('div');
    cardHtml.className = 'card-item';
    
    const imageUrl = card.image_url || 'placeholder.jpg'; 

    cardHtml.innerHTML = `
        <img src="${imageUrl}" alt="${card.name}">
        <strong>${card.name}</strong>
        
        <p style="font-size: 0.9em; margin: 5px 0;">Set: ${card.set || 'Unknown Set'}</p> 
        <p class="card-detail">Type: <span class="detail-value">${card.type || 'N/A'}</span></p>
        <p class="card-detail">Rarity: <span class="detail-value">${card.rarity || 'N/A'}</span></p>
        <p class="card-detail">ID: <span class="detail-value">${card.id || 'N/A'}</span></p>
        
        ${isCollection 
            ? `
                <button class="delete-btn" onclick="deleteCard('${card.id}')">Delete</button>
              `
            : `
                <button onclick='addToCollection(${JSON.stringify(card)})'>Add to collection</button>
              `
        }
    `;
    return cardHtml;
}

// ------------------------------------------------------------------
// GESTIONE COLLEZIONE (Caricamento Iniziale e Filtro)
// ------------------------------------------------------------------

// ⬅️ La funzione ora accetta il parametro di ricerca dal campo input
async function loadCollection(searchQuery = '') { 
    const container = document.getElementById('collection-results-container');
    const inputElement = document.getElementById('collection-search-input');
    
    container.innerHTML = '';
    
    let endpoint = 'collection';
    let statusMessage = 'Caricamento collezione completa...';
    
    // 1. Applica il filtro se l'input non è vuoto
    if (searchQuery && searchQuery.trim() !== '') {
        const cleanedQuery = searchQuery.trim();
        endpoint = `collection?name=${encodeURIComponent(cleanedQuery)}`;
        statusMessage = `Ricerca collezione per "${cleanedQuery}" in corso...`;
    } 
    
    setStatus('collection-status', statusMessage);
    
    try {
        const collection = await fetchData(endpoint);
        
        if (collection.length === 0) {
            const emptyMsg = searchQuery ? `Nessuna carta trovata con il nome "${searchQuery}".` : `La tua collezione è vuota.`;
            setStatus('collection-status', emptyMsg, true);
            return;
        }
        
        // 2. Rendering dei risultati
        collection.forEach(card => {
            container.appendChild(renderCard(card, true)); 
        });
        
        setStatus('collection-status', `${collection.length} carte trovate.`, false);

    } catch (error) {
        setStatus('collection-status', error.message, true);
    }
}

// ⬅️ Nuova funzione per resettare il campo di ricerca e ricaricare tutto
function clearCollectionSearch() {
    const inputElement = document.getElementById('collection-search-input');
    if (inputElement) {
        inputElement.value = ''; // Pulisce il campo
    }
    loadCollection(); // Chiama il caricamento senza query
}

// ------------------------------------------------------------------
// 1. RICERCA ESTERNA (GET)
// ------------------------------------------------------------------

async function handleSearchResults(endpoint, query, containerId, statusId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    setStatus(statusId, `Loading results for "${query}"...`);
    
    try {
        const data = await fetchData(endpoint);
        
        // Se la ricerca per ID restituisce un singolo oggetto (non un array)
        let results = Array.isArray(data) ? data : [data];
        
        if (results.length === 0 || !results[0].id) {
            setStatus(statusId, `No results availiable for this card.`, true);
            return;
        }
        
        // FASE DI NORMALIZZAZIONE DEI DATI
        results.forEach(card => {
            // Se card.set è un oggetto (ovvero, proviene da una ricerca ID completa)
            if (typeof card.set === 'object' && card.set !== null) {
                card.set = card.set.name || 'Unknown Set';
            }
            
            // Passa l'oggetto normalizzato al rendering
            container.appendChild(renderCard(card)); 
        });
        
        setStatus(statusId, `${results.length} availiable results.`, false);

    } catch (error) {
        setStatus(statusId, error.message, true);
    }
}

/** * Ricerca per Nome: Chiama /api/tcg/search_name?name=query */
function handleSearchByName() {
    const query = document.getElementById('search-input-name').value.trim();
    if (query) {
        const endpoint = `tcg/search_name?name=${query}`;
        handleSearchResults(endpoint, query, 'search-results-container', 'search-status');
    }
}

/** * Ricerca per ID: Chiama /api/tcg/search_id?id=cardId */
function handleSearchById() {
    const cardId = document.getElementById('search-input-id').value.trim();
    if (!cardId) return;

    const endpoint = `tcg/search_id?id=${cardId}`; 
    handleSearchResults(endpoint, cardId, 'search-results-container', 'search-status');
}

// ------------------------------------------------------------------
// 2. GESTIONE COLLEZIONE (POST, GET, DELETE)
// ------------------------------------------------------------------

async function addToCollection(cardData) {
    
    try {
        const response = await fetch(`${API_BASE_URL}/collection`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cardData), 
        });

        const result = await response.json();
        
        if (response.status === 201) {
            alert(`${result.message}`);
        } else {
            alert(`Error/Conflict: ${result.message}`); 
        }
        
        loadCollection(); 

    } catch (error) {
        console.error('Error during the saving:', error);
        alert('Not able to connect to the server.');
    }
}

async function loadCollection(searchQuery = '') { 
    const container = document.getElementById('collection-results-container');
    const inputElement = document.getElementById('collection-search-input');
    
    // Pulizia e stato iniziale
    container.innerHTML = '';
    
    let endpoint = 'collection';
    let statusMessage = 'Collection loaded...';
    
    // 1. Logica di Filtraggio e Costruzione Endpoint
    if (searchQuery && searchQuery.trim() !== '') {
        const cleanedQuery = searchQuery.trim();
        // Codifica il valore per URL
        endpoint = `collection?name=${encodeURIComponent(cleanedQuery)}`;
        statusMessage = `Searching "${cleanedQuery}" in the collection...`;
    } 
    
    setStatus('collection-status', statusMessage); // Mostra lo stato di attesa
    
    // 2. Esecuzione della Richiesta API
    try {
        const collection = await fetchData(endpoint);
        
        // 3. Gestione dei Risultati
        
        if (collection.length === 0) {
            const emptyMsg = searchQuery ? `Nessuna carta trovata con il nome "${searchQuery}".` : `La tua collezione è vuota. Aggiungi nuove carte!`;
            setStatus('collection-status', emptyMsg, true); // True per indicare che è un messaggio di esito (sebbene vuoto)
            return;
        }

        // 4. Rendering Sicuro dei Risultati
        collection.forEach(card => {
            // Se una carta dovesse fallire, l'errore verrà catturato all'esterno del loop
            container.appendChild(renderCard(card, true)); 
        });
        
        setStatus('collection-status', `${collection.length} cards availiable.`, false);

    } catch (error) {
        // Cattura errori di rete, parsing JSON o fallimenti del server (500/503)
        setStatus('collection-status', error.message, true);
    }
}

async function deleteCard(cardId) {
    if (!confirm(`Are you sure you want to remove card: ${cardId}?`)) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/collection?id=${cardId}`, {
            method: 'DELETE',
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(result.message);
            loadCollection(); 
        } else {
             alert(`Errore: ${result.message}`);
        }

    } catch (error) {
        console.error('Error during deleting:', error);
        alert('Connection Error during deleting.');
    }
}

function clearCollectionSearch() {
    const inputElement = document.getElementById('collection-search-input');
    if (inputElement) {
        inputElement.value = ''; // Pulisce il campo
    }
    loadCollection(); // Ricarica senza filtro
}

// ⬅️ Esegui il caricamento iniziale DOPO che il DOM è pronto.
document.addEventListener('DOMContentLoaded', () => {
    // Controlla se l'utente è nella scheda collezione (se è il default) e carica.
    // In questo caso, lo carichiamo solo quando viene cliccato il tab (vedi showTab()).
});