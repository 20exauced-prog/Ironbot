# Mise En Ligne D'Ironbot

## Option recommandee

La voie la plus simple et la plus safe pour toi est `Render + PostgreSQL gere`.

Pourquoi je choisis cette option:
- Render gere automatiquement le HTTPS/TLS et le renouvelle.
- Les deploiements sont simples et peuvent etre relies a GitHub.
- La base PostgreSQL geree est plus adaptee et plus sure qu'un `sqlite` expose sur un serveur public.
- Tu evites une grosse partie des erreurs de configuration systeme d'un VPS classique.

Ce guide prepare une mise en ligne simple et propre sur un VPS Linux avec `nginx` + `gunicorn`.

## Deploiement Render recommande

### 1. Mettre le projet sur GitHub

Render deploye le plus simplement depuis un repository Git.

### 2. Connecter le repo a Render

Dans Render:
- clique sur `New`
- choisis `Blueprint`
- connecte ton repo GitHub
- Render detectera le fichier [render.yaml](/Users/exaucedogble/sitebot/render.yaml#L1)

### 3. Lancer le blueprint

Le blueprint cree:
- un service web Ironbot
- une base PostgreSQL geree

Render utilisera:
- [build.sh](/Users/exaucedogble/sitebot/build.sh#L1) pour installer les dependances, collecter les fichiers statiques et faire les migrations
- [gunicorn.conf.py](/Users/exaucedogble/sitebot/gunicorn.conf.py#L1) pour lancer Django

### 4. Configurer le domaine

Une fois le premier deploy termine:
- ouvre ton service sur Render
- ajoute ton domaine custom
- Render genere et renouvelle le certificat TLS automatiquement

### 5. Regler les variables importantes

Dans Render, adapte au minimum:
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_ADMIN_PATH`

Quand tu auras ton vrai domaine, remplace les valeurs `ironbot.onrender.com` par ce domaine.

### 6. Verifications apres mise en ligne

- ouvre `/health/`
- teste l'inscription et la connexion
- verifie que l'admin custom n'est pas sur `/admin/`
- connecte-toi avec `Exauced@`
- verifie que le logo et les styles sont bien servis

### 7. Modifier le site plus tard

Oui, tu pourras toujours modifier le site apres mise en ligne:
- tu modifies en local
- tu pushes sur GitHub
- Render redeploie automatiquement

Si tu veux etre plus prudent:
- travaille sur une branche
- teste localement
- merge ensuite sur la branche de production

---

## Option alternative: VPS

Je te laisse aussi l'option VPS ci-dessous si un jour tu veux un controle maximal, mais je ne la recommande pas comme premier choix pour toi aujourd'hui.

## 1. Preparer le serveur

Installe Python, `venv`, `nginx` et `git`.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git
```

## 2. Recuperer le projet

```bash
sudo mkdir -p /srv/ironbot
sudo chown $USER:$USER /srv/ironbot
cd /srv/ironbot
git clone <ton-repo-git> current
python3 -m venv /srv/ironbot/venv
source /srv/ironbot/venv/bin/activate
pip install --upgrade pip
pip install -r /srv/ironbot/current/requirements.txt
```

## 3. Configurer l'environnement

Copie `.env.example` dans un vrai fichier `.env`.

```bash
cp /srv/ironbot/current/.env.example /srv/ironbot/shared.env
```

Exemple minimal:

```env
DJANGO_SECRET_KEY=remplace-par-une-cle-longue-et-secrete
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=ironbot.example.com,www.ironbot.example.com
DJANGO_ADMIN_PATH=exauced-control-2026/
DJANGO_CSRF_TRUSTED_ORIGINS=https://ironbot.example.com,https://www.ironbot.example.com
DJANGO_LOGIN_RATE_LIMIT_ATTEMPTS=7
DJANGO_LOGIN_RATE_LIMIT_WINDOW_SECONDS=900
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
```

## 4. Preparer la base et les fichiers statiques

```bash
cd /srv/ironbot/current
source /srv/ironbot/venv/bin/activate
export $(grep -v '^#' /srv/ironbot/shared.env | xargs)
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 5. Configurer `systemd`

Copie le fichier [ironbot.service.example](/Users/exaucedogble/sitebot/deploy/ironbot.service.example#L1) dans `/etc/systemd/system/ironbot.service`
et adapte les chemins si besoin.

```bash
sudo cp /srv/ironbot/current/deploy/ironbot.service.example /etc/systemd/system/ironbot.service
sudo systemctl daemon-reload
sudo systemctl enable ironbot
sudo systemctl start ironbot
sudo systemctl status ironbot
```

## 6. Configurer `nginx`

Copie [nginx-ironbot.conf.example](/Users/exaucedogble/sitebot/deploy/nginx-ironbot.conf.example#L1) vers `/etc/nginx/sites-available/ironbot`
et remplace le domaine.

```bash
sudo cp /srv/ironbot/current/deploy/nginx-ironbot.conf.example /etc/nginx/sites-available/ironbot
sudo ln -s /etc/nginx/sites-available/ironbot /etc/nginx/sites-enabled/ironbot
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Activer HTTPS

Quand le domaine pointe vers ton serveur:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ironbot.example.com -d www.ironbot.example.com
```

## 8. Verifications

- Ouvre `/health/` pour verifier que l'application repond.
- Ouvre l'URL admin definie par `DJANGO_ADMIN_PATH` avec ton compte `Exauced@`.
- Verifie que le logo et les styles s'affichent correctement.

## 9. Mettre a jour plus tard

Tu pourras continuer a modifier le site apres la mise en ligne:

```bash
cd /srv/ironbot/current
git pull
source /srv/ironbot/venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' /srv/ironbot/shared.env | xargs)
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart ironbot
```

## 10. Avant d'ouvrir au public

- Garde une sauvegarde de `db.sqlite3`.
- N'utilise jamais `DJANGO_DEBUG=True` en production.
- Utilise une vraie cle secrete longue.
- Verifie que ton domaine pointe bien vers l'IP du serveur.
- Active le pare-feu du serveur:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

- Installe `fail2ban` pour bloquer les tentatives repetees sur le serveur:

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```
