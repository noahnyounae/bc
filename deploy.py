"""
Configuration et déploiement du contrat ActionChain Token
"""

import smartpy as sp
from ActionChain import main

def deploy_contract():
    """Déploie le contrat ActionChain Token"""
    
    # Configuration des comptes
    admin = sp.test_account("Admin")
    
    # Paramètres du token
    initial_supply = 1_000_000  # 1 million de tokens
    token_name = "ActionChain Token"
    token_symbol = "ACT"
    
    # Création du contrat
    contract = main.ActionChainToken(
        admin=admin.address,
        initial_supply=initial_supply,
        token_name=token_name,
        token_symbol=token_symbol
    )
    
    # Compilation et génération des fichiers de déploiement
    print("Compilation du contrat...")
    scenario = sp.test_scenario("ActionChain Deployment", main)
    scenario += contract
    
    print("Contrat compilé avec succès!")
    print(f"Offre initiale: {initial_supply:,} {token_symbol}")
    print(f"Administrateur: {admin.address}")
    
    return contract

def test_contract_interactions():
    """Teste les interactions avec le contrat"""
    
    scenario = sp.test_scenario("Test des interactions", main)
    
    # Comptes de test
    admin = sp.test_account("Admin")
    alice = sp.test_account("Alice") 
    bob = sp.test_account("Bob")
    charlie = sp.test_account("Charlie")
    
    # Déployer le contrat
    contract = main.ActionChainToken(
        admin=admin.address,
        initial_supply=1_000_000,
        token_name="ActionChain Token",
        token_symbol="ACT"
    )
    scenario += contract
    
    # Étape 1: Mint des tokens pour les utilisateurs
    scenario.h2("🏭 Mint de tokens")
    contract.mint(to_address=alice.address, amount=50_000).run(sender=admin)
    contract.mint(to_address=bob.address, amount=30_000).run(sender=admin)
    contract.mint(to_address=charlie.address, amount=20_000).run(sender=admin)
    
    # Vérification des soldes
    scenario.verify(contract.get_balance(alice.address) == 50_000)
    scenario.verify(contract.get_balance(bob.address) == 30_000)
    scenario.verify(contract.get_balance(charlie.address) == 20_000)
    
    # Étape 2: Ordres de vente
    scenario.h2("💰 Placement d'ordres de vente")
    
    # Alice vend 1000 tokens à 1.25 tez chaque
    contract.place_sell_order(
        price=sp.mutez(1_250_000),  # 1.25 tez en mutez
        quantity=1_000
    ).run(sender=alice)
    
    # Charlie vend 500 tokens à 1.30 tez chaque  
    contract.place_sell_order(
        price=sp.mutez(1_300_000),  # 1.30 tez en mutez
        quantity=500
    ).run(sender=charlie)
    
    # Étape 3: Ordres d'achat (qui déclenchent des trades)
    scenario.h2("Placement d'ordres d'achat")
    
    # Bob achète 500 tokens au prix de marché (1.25 tez)
    contract.place_buy_order(
        price=sp.mutez(1_250_000),  # 1.25 tez en mutez
        quantity=500
    ).run(
        sender=bob,
        amount=sp.tez(625)  # 500 * 1.25 = 625 tez
    )
    
    # Vérification du trade
    scenario.verify(contract.get_balance(alice.address) == 49_500)  # 50_000 - 500
    scenario.verify(contract.get_balance(bob.address) == 30_500)    # 30_000 + 500
    
    # Bob achète encore 300 tokens à un prix plus élevé
    contract.place_buy_order(
        price=sp.mutez(1_300_000),  # 1.30 tez en mutez  
        quantity=300
    ).run(
        sender=bob,
        amount=sp.tez(390)  # 300 * 1.30 = 390 tez
    )
    
    # Étape 4: Ordre d'achat sans correspondance
    scenario.h2("Ordre d'achat en attente")
    
    # Bob place un ordre d'achat à un prix plus bas
    contract.place_buy_order(
        price=sp.mutez(1_200_000),  # 1.20 tez en mutez
        quantity=200
    ).run(
        sender=bob,
        amount=sp.tez(240)  # 200 * 1.20 = 240 tez
    )
    
    # Étape 5: Annulation d'ordre
    scenario.h2("Annulation d'ordre")
    
    # Bob annule son dernier ordre d'achat
    contract.cancel_order(
        order_id=3,  # ID du dernier ordre
        order_type="buy"
    ).run(sender=bob)
    
    # Étape 6: Test des transferts
    scenario.h2("Transferts de tokens")
    
    # Alice transfère 1000 tokens à Charlie
    contract.transfer(
        to_address=charlie.address,
        amount=1_000
    ).run(sender=alice)
    
    scenario.verify(contract.get_balance(alice.address) == 48_500)  # 49_500 - 1_000
    scenario.verify(contract.get_balance(charlie.address) == 20_800) # 20_000 + 300 + 500 (achat) + 1_000
    
    # Étape 7: Test de burn
    scenario.h2("Burn de tokens")
    
    # Charlie burn 500 tokens
    contract.burn(amount=500).run(sender=charlie)
    scenario.verify(contract.get_balance(charlie.address) == 20_300)
    scenario.verify(contract.get_total_supply() == 999_500)  # 1_000_000 - 500
    
    scenario.h2("Tests terminés avec succès!")

def generate_deployment_files():
    """Génère les fichiers nécessaires pour le déploiement"""
    
    print("Génération des fichiers de déploiement...")
    
    # Script de déploiement
    deployment_script = """
# Script de déploiement pour ActionChain Token

## Prérequis
1. Installer Taquito CLI: `npm install -g @taquito/cli`
2. Avoir un wallet Tezos configuré
3. Avoir des fonds XTZ pour le déploiement

## Étapes de déploiement

### 1. Compiler le contrat
```bash
smartpy compile ActionChain.py output/
```

### 2. Déployer sur le testnet
```bash
taquito deploy output/ActionChain_compiled.tz \\
    --storage '{"admin": "tz1...", "total_supply": 1000000, ...}' \\
    --network ghostnet
```

### 3. Vérifier le déploiement
```bash
taquito get-contract KT1... --network ghostnet
```

## Configuration du frontend

1. Mettre à jour l'adresse du contrat dans `web/script.js`
2. Configurer le RPC endpoint
3. Tester les interactions

## Exemples d'interaction

### Mint de tokens (admin seulement)
```javascript
await contract.methods.mint("tz1...", 10000).send()
```

### Placer un ordre d'achat
```javascript
await contract.methods.place_buy_order(1250000, 100).send({
    amount: 125  // 100 * 1.25 tez
})
```

### Placer un ordre de vente  
```javascript
await contract.methods.place_sell_order(1300000, 50).send()
```
"""
    
    with open("deployment_guide.md", "w") as f:
        f.write(deployment_script)
    
    # Configuration pour le frontend
    config_js = """
// Configuration ActionChain Token

const CONFIG = {
    // Adresse du contrat (à mettre à jour après déploiement)
    CONTRACT_ADDRESS: 'KT1...',
    
    // Configuration réseau
    NETWORK: {
        name: 'ghostnet',  // ou 'mainnet' pour la production
        rpc: 'https://ghostnet.smartpy.io'
    },
    
    // Paramètres du token
    TOKEN: {
        name: 'ActionChain Token',
        symbol: 'ACT',
        decimals: 6
    },
    
    // Limites et contraintes
    LIMITS: {
        minOrderQuantity: 1,
        maxOrderQuantity: 1000000,
        minPrice: 0.01,  // 0.01 tez
        maxPrice: 1000,  // 1000 tez
        priceDecimals: 2 // Maximum 2 décimales
    },
    
    // Interface utilisateur
    UI: {
        refreshInterval: 5000,  // 5 secondes
        chartUpdateInterval: 30000,  // 30 secondes
        maxOrderbookOrders: 10,
        maxTradeHistory: 50
    }
};

// Export de la configuration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else {
    window.ACTIONCHAIN_CONFIG = CONFIG;
}
"""
    
    with open("web/config.js", "w") as f:
        f.write(config_js)
    
    print("Fichiers générés:")
    print("  - deployment_guide.md")
    print("  - web/config.js")

if __name__ == "__main__":
    print("ActionChain Token - Configuration de déploiement")
    print("=" * 50)
    
    # Déployer et tester le contrat
    contract = deploy_contract()
    test_contract_interactions()
    generate_deployment_files()
    
    print("\nConfiguration terminée!")
    print("\nProchaines étapes:")
    print("1. Compiler le contrat avec SmartPy")
    print("2. Déployer sur Tezos (testnet puis mainnet)")
    print("3. Mettre à jour l'adresse du contrat dans web/config.js")
    print("4. Lancer le site web")
