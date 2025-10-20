console.log('Script event_registration.js chargé');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM chargé, initialisation du formulaire d\'inscription...');
    
    const form = document.getElementById('eventRegistrationForm');
    if (!form) {
        console.error('Erreur: Le formulaire avec l\'ID eventRegistrationForm n\'a pas été trouvé');
        return;
    }
    
    const modalElement = document.getElementById('registrationModal');
    if (!modalElement) {
        console.error('Erreur: L\'élément #registrationModal n\'a pas été trouvé dans le DOM');
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    console.log('Modal initialisé avec succès');
    
    // Gestion de la soumission du formulaire
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');
        const btnText = submitBtn.querySelector('.btn-text');
        
        // Désactiver le bouton et afficher le spinner
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        btnText.textContent = 'Traitement...';
        
        try {
            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });
            
            if (!response.ok) {
                // Si la réponse n'est pas OK, essayer de récupérer les données d'erreur
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Erreur HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Réponse du serveur:', data);
            
            if (data.success) {
                // Afficher un message de succès
                const successAlert = `
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        ${data.message || 'Votre inscription a bien été enregistrée !'}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                `;
                
                // Insérer l'alerte avant le formulaire
                form.insertAdjacentHTML('beforebegin', successAlert);
                
                // Fermer le modal après un court délai
                setTimeout(() => {
                    if (modal && typeof modal.hide === 'function') {
                        modal.hide();
                    }
                    // Supprimer l'alerte après 5 secondes
                    const alert = document.querySelector('.alert');
                    if (alert) {
                        setTimeout(() => alert.remove(), 5000);
                    }
                }, 1000);
                
                // Réinitialiser le formulaire
                form.reset();
            } else {
                // Afficher les erreurs de validation
                if (data.errors) {
                    console.error('Erreurs de validation:', data.errors);
                    // Réinitialiser les erreurs précédentes
                    form.querySelectorAll('.is-invalid').forEach(el => {
                        el.classList.remove('is-invalid');
                    });
                    
                    // Afficher les nouvelles erreurs
                    Object.entries(data.errors).forEach(([field, errors]) => {
                        const input = document.getElementById(`id_${field}`);
                        if (input) {
                            input.classList.add('is-invalid');
                            let feedback = input.nextElementSibling;
                            
                            // Si l'élément suivant n'est pas un feedback, on essaie de le trouver
                            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                                const parent = input.closest('.form-group') || input.parentElement;
                                feedback = parent.querySelector('.invalid-feedback');
                            }
                            
                            if (feedback && feedback.classList.contains('invalid-feedback')) {
                                feedback.textContent = Array.isArray(errors) ? errors[0] : errors;
                                feedback.style.display = 'block';
                            }
                        }
                    });
                } else if (data.message) {
                    // Afficher un message d'erreur général
                    alert(data.message);
                }
            }
        } catch (error) {
            console.error('Erreur détaillée:', {
                name: error.name,
                message: error.message,
                stack: error.stack,
                response: error.response
            });
            
            // Afficher un message d'erreur plus détaillé
            const errorMessage = error.message || 'Une erreur est survenue. Veuillez réessayer.';
            
            // Afficher l'erreur dans une alerte stylisée
            const errorHtml = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>Erreur :</strong> ${errorMessage}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
            `;
            
            // Insérer l'alerte d'erreur avant le formulaire
            form.insertAdjacentHTML('beforebegin', errorHtml);
            
            // Faire défiler jusqu'à l'erreur
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        } finally {
            // Réactiver le bouton
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
            btnText.textContent = "S'inscrire";
        }
    });
    
    // Réinitialiser le formulaire à l'ouverture du modal
    document.getElementById('registrationModal').addEventListener('show.bs.modal', function () {
        form.reset();
        // Réinitialiser les erreurs
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    });
});
