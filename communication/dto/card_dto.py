
class CardDTO:
    """
    Data Transfer Object (DTO) per una Carta Pokémon. 
    Definisce il contratto dei dati tra i livelli.
    """

    def __init__(self, 
                 id: str, 
                 name: str, 
                 image_url: str, 
                 set_name: str = 'N/A', 
                 set_id: str = 'N/A',
                 type: str = 'N/A', 
                 rarity: str = 'N/A'):
        
        self.id = id
        self.name = name
        self.image_url = image_url
        
        # Dati dettagliati (possono essere N/A per ricerche brevi)
        self.set_name = set_name
        self.set_id = set_id
        self.type = type
        self.rarity = rarity
        
    def to_dict(self):
        """Converte l'oggetto in un dizionario per la serializzazione JSON di Flask."""
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
            'set': self.set_name,        # Usato dal frontend per visualizzare
            'set_id': self.set_id,       # Usato dal DataManager per la Foreign Key
            'type': self.type,
            'rarity': self.rarity,
        }