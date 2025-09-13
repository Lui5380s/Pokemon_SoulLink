document.addEventListener('DOMContentLoaded', function() {
    // Dynamisches Laden von Pokémon-Kartenbildern
    document.querySelectorAll('.pokemon-card-img').forEach(img => {
        const pokemonName = img.alt;
        
        // Fallback, falls das Bild nicht geladen werden kann
        img.onerror = function() {
            this.src = 'https://placehold.co/100x140/ef4444/white?text=❓';
            this.onerror = null;
        };
    });
    
    // Erweiterte Funktionalität für Kartenvorschau
    const cardPreviews = document.querySelectorAll('.card-preview');
    cardPreviews.forEach(card => {
        card.addEventListener('click', function() {
            // Vergrößerte Ansicht der Karte anzeigen
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.alt}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${this.src}" alt="${this.alt}" class="img-fluid">
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            
            // Modal entfernen, nachdem es geschlossen wurde
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        });
    });
});