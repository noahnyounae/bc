# 🔗 ActionChain Token

**Un token par actions avec système d'ordres intégré sur Tezos**

ActionChain Token (ACT) est un smart contract innovant qui combine un token standard avec un système de carnet d'ordres (orderbook) décentralisé. Il permet aux utilisateurs de trader des tokens directement sur la blockchain avec correspondance automatique des ordres.

## Fonctionnalités

### Token Standard
- **Mint/Burn** : L'administrateur peut créer ou détruire des tokens
- **Transferts** : Transferts standard entre adresses
- **Soldes** : Gestion des soldes avec vues on-chain
- **Offre contrôlée** : Offre totale redéfinissable par l'admin

### Système d'Ordres
- **Ordres d'achat** : Placer des ordres avec paiement en Tezos
- **Ordres de vente** : Vendre ses tokens au prix souhaité
- **Correspondance automatique** : Les ordres compatibles sont exécutés automatiquement
- **Prix précis** : Contrainte de 2 décimales maximum pour optimiser les correspondances
- **Annulation** : Possibilité d'annuler ses ordres avec remboursement

### Statistiques & Suivi
- **Prix actuel** : Dernier prix d'échange
- **Volume 24h** : Volume de trading sur 24 heures (reset automatique)
- **Historique** : Enregistrement de tous les trades
- **Carnet d'ordres** : Visualisation des ordres en attente

## Architecture

### Smart Contract (`ActionChain.py`)
```
ActionChainToken
├── Token Functions
│   ├── mint()          # Création de tokens (admin)
│   ├── burn()          # Destruction de tokens
│   └── transfer()      # Transferts
├── Trading Functions
│   ├── place_buy_order()   # Placer ordre d'achat
│   ├── place_sell_order()  # Placer ordre de vente
│   ├── cancel_order()      # Annuler un ordre
│   └── match_orders()      # Correspondance automatique
└── Views
    ├── get_balance()       # Solde d'une adresse
    ├── get_total_supply()  # Offre totale
    ├── get_last_price()    # Dernier prix
    └── get_volume_24h()    # Volume 24h
```

### Interface Web (`web/`)
- **index.html** : Interface utilisateur complète
- **styles.css** : Design moderne et responsive
- **script.js** : Logique de trading et intégration blockchain
- **config.js** : Configuration du contrat et paramètres

## Installation & Déploiement

### Prérequis
```bash
# Installer SmartPy
pip install https://smartpy.io/static/tezos_smartpy-0.22.0-py3-none-any.whl

# Installer Node.js pour l'interface web
npm install -g @taquito/cli
npm install -g http-server
```

### 1. Compiler le contrat
```bash
smartpy compile ActionChain.py output/
```

### 2. Tests locaux
```bash
python deploy.py
```

### 3. Déploiement sur testnet
```bash
# Mettre à jour les paramètres dans deploy.py
# Puis déployer
smartpy deploy output/ --network ghostnet
```

### 4. Lancer l'interface web
```bash
cd web/
# Mettre à jour l'adresse du contrat dans config.js
http-server . -p 8080
```

## Utilisation

### Pour les Administrateurs
```python
# Mint de nouveaux tokens
contract.mint(to_address="tz1...", amount=10000)

# Configuration initiale
initial_supply = 1_000_000
token_name = "ActionChain Token"
token_symbol = "ACT"
```

### Pour les Traders
```python
# Placer un ordre d'achat (100 tokens à 1.25 tez chaque)
contract.place_buy_order(
    price=sp.mutez(1_250_000),  # 1.25 tez en mutez
    quantity=100
).run(amount=sp.tez(125))  # Total: 125 tez

# Placer un ordre de vente (50 tokens à 1.30 tez chaque)
contract.place_sell_order(
    price=sp.mutez(1_300_000),  # 1.30 tez en mutez
    quantity=50
)

# Annuler un ordre
contract.cancel_order(order_id=5, order_type="buy")
```

## Fonctionnement Technique

### Correspondance des Ordres
1. **Placement** : Un utilisateur place un ordre (achat/vente)
2. **Vérification** : Contrôle des fonds et des soldes
3. **Correspondance** : Recherche d'ordres compatibles
4. **Exécution** : Transfer automatique des tokens et tezos
5. **Mise à jour** : Actualisation du carnet d'ordres

### Contraintes de Prix
- **2 décimales max** : Les prix doivent être multiples de 0.01 tez
- **Validation** : `price % 10000 == 0` (en mutez)
- **Optimisation** : Augmente les chances de correspondance

### Sécurité
- **Vérifications** : Soldes suffisants avant exécution
- **Atomicité** : Transactions tout-ou-rien
- **Remboursements** : Annulation sécurisée avec remboursement automatique

## Interface Web

### Fonctionnalités
- **Graphique des prix** en temps réel
- **Carnet d'ordres** avec spread
- **Interface de trading** intuitive  
- **Statistiques du marché** complètes
- **Historique des transactions**
- **Intégration wallet** Tezos

### Technologies
- **Chart.js** pour les graphiques
- **CSS Grid/Flexbox** pour le layout
- **Vanilla JavaScript** pour les interactions
- **Taquito** pour l'intégration Tezos

## Cas d'Usage

### 1. Token d'Actions d'Entreprise
- Émission de tokens représentant des actions
- Trading décentralisé sans intermédiaire
- Transparence totale des transactions

### 2. Token de Gouvernance
- Distribution de tokens de vote
- Marché secondaire pour les tokens
- Prix déterminé par l'offre et la demande

### 3. Token de Récompense
- Système de récompenses économique
- Possibilité de revendre les récompenses
- Création d'un écosystème économique

## Exemples de Données

### Structure d'un Ordre
```python
order = {
    "trader": "tz1...",
    "order_type": "buy",  # ou "sell"
    "price": 1_250_000,   # 1.25 tez en mutez
    "quantity": 100,
    "timestamp": "2025-01-08T14:30:00Z"
}
```

### Structure d'un Trade
```python
trade = {
    "buyer": "tz1...",
    "seller": "tz1...", 
    "price": 1_250_000,   # Prix d'exécution
    "quantity": 50,
    "timestamp": "2025-01-08T14:30:15Z"
}
```

## Évolutions Futures

### V2.0 - Fonctionnalités Avancées
- **Ordres conditionnels** (stop-loss, take-profit)
- **Trading algorithmique** avec API
- **Pool de liquidité** pour améliorer la liquidité
- **Staking de tokens** pour des récompenses

### V3.0 - DeFi Integration
- **Intégration DEX** avec d'autres plateformes
- **Yield farming** sur les tokens
- **Prêts/Emprunts** avec tokens en collatéral
- **Options et dérivés** sur le token

## Contribution

Les contributions sont les bienvenues ! Merci de :

1. **Fork** le projet
2. Créer une **branche** pour votre fonctionnalité
3. **Commiter** vos changements
4. **Ouvrir une Pull Request**

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
---

**ActionChain Token - L'avenir du trading décentralisé sur Tezos**
