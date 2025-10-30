# Liyok Green - Site Web Django

## Description du projet

Liyok Green est un site web Django moderne et responsive dédié à la promotion de solutions écologiques et durables. Le site présente les services, projets et initiatives de l'entreprise dans le domaine de l'environnement.

## Fonctionnalités principales

### 🏠 Page d'accueil
- Slider hero avec images défilantes et couverture noire
- Présentation des services principaux
- Sectionvaleurs de l'entreprise
- Témoignages clients
- Galerie de projets

### 📋 Gestion des services
- Liste des services avec images
- Pages de détail pour chaque service
- Médias associés (images, vidéos)
- Catégorisation des services

### 📄 Système d'articles
- Blog avec articles publiés
- Catégorisation des articles
- Gestion des tags
- Recherche et filtrage

### 🖼️ Galeries
- Organisation par catégories
- Affichage en grille responsive
- Lightbox pour visualisation
- Gestion des images

### 📅 Événements
- Calendrier des événements
- Système d'inscription
- Gestion des participants
- Médias associés

### 📄 Documents PDF
- Bibliothèque de documents téléchargeables
- Compteur de téléchargements
- Organisation par catégories
- Gestion des droits d'accès

### 👥 Équipe
- Présentation des membres
- Rôles et descriptions
- Photos de profil

### 📞 Contact
- Formulaire de contact
- Informations de contact
- Intégration email

## Technologies utilisées

- **Backend**: Django 5.0
- **Base de données**: SQLite (développement) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework CSS**: Bootstrap 5 + CSS personnalisé
- **Animations**: WOW.js, Slick Slider
- **Admin**: Django Unfold (interface moderne)
- **Médias**: Gestion intégrée des images et fichiers

## Installation et configuration

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)

### Installation

1. **Cloner le repository**
```bash
git clone <url-du-repo>
cd liyok-green
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de la base de données**
```bash
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

Le site sera accessible sur `http://127.0.0.1:8000/`
L'admin sera accessible sur `http://127.0.0.1:8000/admin/`
Le username Admin est `admin`
Le password Admin est `admin123`
## Structure du projet

```
liyok-green/
├── Liyok/                    # Configuration Django
│   ├── settings.py          # Paramètres principaux
│   ├── urls.py              # Routes principales
│   └── wsgi.py
├── managments/               # Application principale
│   ├── models.py            # Modèles de données
│   ├── views.py             # Logique métier
│   ├── urls.py              # Routes de l'app
│   ├── admin.py             # Configuration admin
│   ├── forms.py             # Formulaires
│   └── templates/           # Templates HTML
├── users/                    # Gestion utilisateurs
├── static/                   # Fichiers statiques
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
├── media/                    # Fichiers uploadés
├── templates/                # Templates globaux
└── requirements.txt          # Dépendances Python
```

## Modèles de données

### Principaux modèles

- **SiteSetting**: Configuration générale du site
- **Service**: Services proposés
- **Article**: Articles de blog
- **Category**: Catégorisation
- **Galerie**: Galeries d'images
- **Event**: Événements
- **Document**: Documents PDF
- **TeamMember**: Membres de l'équipe
- **ContactMessage**: Messages de contact

## Administration

Le site utilise Django Unfold pour une interface d'administration moderne et intuitive.

### Fonctionnalités admin
- Gestion complète de tous les contenus
- Upload et gestion des médias
- Interface responsive
- Aperçus d'images
- Statistiques de base

## Déploiement

### Configuration production

1. **Variables d'environnement**
```bash
DEBUG=False
SECRET_KEY=votre-cle-secrete
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=votre-domaine.com
```

2. **Collecte des fichiers statiques**
```bash
python manage.py collectstatic
```

3. **Configuration du serveur web**
- Nginx + Gunicorn recommandé
- Configuration SSL obligatoire

## Fonctionnalités à implémenter

- [ ] Optimisation des images (compression WebP)
- [ ] Validation JavaScript côté client
- [ ] Configuration des emails
- [ ] Pagination des listes longues
- [ ] SEO (meta tags, sitemap)
- [ ] Google Analytics
- [ ] Cache Django
- [ ] Tests unitaires

## Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou suggestion :
- Email: contact@liyok-green.com
- Site web: https://liyok-green.com

---

**Développé avec ❤️ pour un avenir plus vert**