import json
import uuid
import random
from datetime import datetime, timedelta

# --- Configuration du volume ---
NUM_LOGS = 50000 
NUM_USERS = 5000
NUM_PRODUCTS = 100

def generate_log_data():
    """Génère une liste de logs pour l'e-commerce."""
    logs = []
    
    # Listes de valeurs possibles
    events = ["VIEW_PRODUCT", "ADD_TO_CART", "PURCHASE", "ERROR_404", "LOGOUT", "SEARCH"]
    products = [f"PROD_{i:03d}" for i in range(1, NUM_PRODUCTS + 1)]
    users = list(range(1, NUM_USERS + 1))
    
    start_time = datetime(2025, 10, 1, 0, 0, 0)

    for _ in range(NUM_LOGS):
        event_type = random.choice(events)
        
        # Simuler un horodatage croissant
        log_time = start_time + timedelta(seconds=random.randint(1, 3600*24*30)) 
        
        log = {
            "log_id": str(uuid.uuid4()),
            "timestamp": log_time.isoformat(),
            "user_id": random.choice(users),
            "event_type": event_type,
            "product_id": random.choice(products) if "PRODUCT" in event_type or "CART" in event_type else None,
            "session_duration_ms": random.randint(100, 60000),
            "description": f"Event {event_type} processed.",
        }
        
        if event_type == "ERROR_404":
            log["description"] = "Page introuvable. Erreur critique."
        elif event_type == "PURCHASE":
            log["description"] = f"Transaction finale réussie pour produit {log['product_id']}."
            
        logs.append(log)
        
    return logs

if __name__ == "__main__":
    data = generate_log_data()

    # Sauvegarde dans le dossier scripts (monté dans Docker)
    with open("/app/scripts/ecommerce_logs.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Génération de {NUM_LOGS} logs terminée. Fichier 'ecommerce_logs.json' créé.")
