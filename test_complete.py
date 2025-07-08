"""
Tests complets pour ActionChain Token
"""

import smartpy as sp
from ActionChain import main

@sp.add_test()
def test_complete_trading_scenario():
    """Test complet d'un scénario de trading réaliste"""
    
    scenario = sp.test_scenario("Scénario de Trading Complet", main)
    
    # === SETUP ===
    # Comptes de test
    admin = sp.test_account("Admin")
    alice = sp.test_account("Alice")   # Market maker
    bob = sp.test_account("Bob")       # Trader actif
    charlie = sp.test_account("Charlie") # Investisseur long terme
    dave = sp.test_account("Dave")     # Day trader
    
    scenario.h1("Configuration initiale")
    
    # Déploiement du contrat
    contract = main.ActionChainToken(
        admin=admin.address,
        initial_supply=2_000_000,  # 2M tokens
        token_name="ActionChain Token",
        token_symbol="ACT"
    )
    scenario += contract
    
    # Distribution initiale des tokens
    scenario.h2("Distribution des tokens")
    contract.mint(to_address=alice.address, amount=100_000).run(sender=admin)   # Market maker
    contract.mint(to_address=bob.address, amount=50_000).run(sender=admin)      # Trader
    contract.mint(to_address=charlie.address, amount=75_000).run(sender=admin)  # Investisseur
    contract.mint(to_address=dave.address, amount=25_000).run(sender=admin)     # Day trader
    
    # Vérification des soldes initiaux
    scenario.verify(contract.get_balance(alice.address) == 100_000)
    scenario.verify(contract.get_balance(bob.address) == 50_000)
    scenario.verify(contract.get_balance(charlie.address) == 75_000)
    scenario.verify(contract.get_balance(dave.address) == 25_000)
    scenario.verify(contract.get_total_supply() == 2_250_000)  # 2M + 250k distribués
    
    # === PHASE 1: CRÉATION DU MARCHÉ ===
    scenario.h1("Phase 1: Création du marché")
    
    # Alice (market maker) crée de la liquidité avec plusieurs ordres
    scenario.h2("Alice crée de la liquidité")
    
    # Ordres de vente échelonnés
    contract.place_sell_order(price=sp.mutez(1_100_000), quantity=500).run(sender=alice)  # 1.10 tez
    contract.place_sell_order(price=sp.mutez(1_150_000), quantity=750).run(sender=alice)  # 1.15 tez
    contract.place_sell_order(price=sp.mutez(1_200_000), quantity=1000).run(sender=alice) # 1.20 tez
    contract.place_sell_order(price=sp.mutez(1_250_000), quantity=1500).run(sender=alice) # 1.25 tez
    
    # Charlie place des ordres d'achat pour créer du support
    scenario.h2("Charlie place des ordres de support")
    contract.place_buy_order(price=sp.mutez(1_050_000), quantity=300).run(
        sender=charlie, amount=sp.tez(315)  # 300 * 1.05 = 315 tez
    )
    contract.place_buy_order(price=sp.mutez(1_000_000), quantity=500).run(
        sender=charlie, amount=sp.tez(500)  # 500 * 1.00 = 500 tez
    )
    contract.place_buy_order(price=sp.mutez(950_000), quantity=1000).run(
        sender=charlie, amount=sp.tez(950)  # 1000 * 0.95 = 950 tez
    )
    
    # === PHASE 2: PREMIERS TRADES ===
    scenario.h1("Phase 2: Premiers échanges")
    
    # Bob achète au marché (prix le plus bas disponible)
    scenario.h2("Bob achète au prix du marché")
    contract.place_buy_order(price=sp.mutez(1_100_000), quantity=200).run(
        sender=bob, amount=sp.tez(220)  # 200 * 1.10 = 220 tez
    )
    
    # Vérification du trade
    scenario.verify(contract.get_balance(alice.address) == 99_700)  # 100_000 - 300 (vendu)
    scenario.verify(contract.get_balance(bob.address) == 50_200)    # 50_000 + 200 (acheté)
    scenario.verify(contract.get_last_price() == sp.mutez(1_100_000))  # Prix du dernier trade
    
    # Dave fait du day trading
    scenario.h2("Dave fait du day trading")
    
    # Dave achète rapidement
    contract.place_buy_order(price=sp.mutez(1_100_000), quantity=300).run(
        sender=dave, amount=sp.tez(330)  # 300 * 1.10 = 330 tez
    )
    
    # Vérification que l'ordre partiel d'Alice a été complètement exécuté
    scenario.verify(contract.get_balance(alice.address) == 99_500)  # 99_700 - 200 restants
    scenario.verify(contract.get_balance(dave.address) == 25_300)   # 25_000 + 300
    
    # Dave revend immédiatement avec profit
    contract.place_sell_order(price=sp.mutez(1_120_000), quantity=250).run(sender=dave)  # +2 centimes
    
    # === PHASE 3: ORDRES COMPLEXES ===
    scenario.h1("Phase 3: Stratégies complexes")
    
    # Bob place un ordre d'achat important à un prix attractif
    scenario.h2("Bob place un gros ordre d'achat")
    contract.place_buy_order(price=sp.mutez(1_150_000), quantity=500).run(
        sender=bob, amount=sp.tez(575)  # 500 * 1.15 = 575 tez
    )
    
    # Cet ordre devrait matcher partiellement avec l'ordre de vente d'Alice à 1.15
    scenario.verify(contract.get_balance(alice.address) == 99_250)  # Vente de 250 tokens
    scenario.verify(contract.get_balance(bob.address) == 50_450)    # Achat de 250 tokens (partiel)
    
    # Alice ajuste ses prix à la baisse
    scenario.h2("Alice ajuste ses prix")
    contract.place_sell_order(price=sp.mutez(1_130_000), quantity=400).run(sender=alice)  # 1.13 tez
    
    # Cela devrait déclencher l'ordre de Bob restant
    scenario.verify(contract.get_balance(bob.address) == 50_700)    # +250 tokens supplémentaires
    
    # === PHASE 4: GESTION DES ORDRES ===
    scenario.h1("Phase 4: Gestion des ordres")
    
    # Dave place un ordre puis l'annule
    scenario.h2("Dave annule un ordre")
    contract.place_buy_order(price=sp.mutez(1_080_000), quantity=100).run(
        sender=dave, amount=sp.tez(108)
    )
    
    # Annulation avec remboursement
    contract.cancel_order(order_id=10, order_type="buy").run(sender=dave)
    
    # Charlie modifie sa stratégie (annule et replace)
    scenario.h2("Charlie modifie sa stratégie")
    contract.cancel_order(order_id=7, order_type="buy").run(sender=charlie)  # Annule ordre à 0.95
    
    # Place un nouvel ordre plus agressif
    contract.place_buy_order(price=sp.mutez(1_080_000), quantity=800).run(
        sender=charlie, amount=sp.tez(864)  # 800 * 1.08 = 864 tez
    )
    
    # === PHASE 5: VOLUME ET STATISTIQUES ===
    scenario.h1("Phase 5: Analyse du volume")
    
    # Série de petits trades pour augmenter le volume
    scenario.h2("Série de trades intensifs")
    
    # Alice et Bob font plusieurs petits échanges
    for i in range(3):
        # Bob achète
        contract.place_buy_order(price=sp.mutez(1_140_000), quantity=50).run(
            sender=bob, amount=sp.tez(57)  # 50 * 1.14 = 57 tez
        )
        
        # Alice replace des ordres de vente
        contract.place_sell_order(price=sp.mutez(1_160_000), quantity=75).run(sender=alice)
    
    # Vérification du volume (approximatif car calculé automatiquement)
    # Le volume devrait inclure tous les trades effectués
    volume = contract.get_volume_24h()
    scenario.verify(volume > 0)
    
    # === PHASE 6: OPÉRATIONS ADMINISTRATIVES ===
    scenario.h1("Phase 6: Opérations administratives")
    
    # Admin mint des tokens supplémentaires
    scenario.h2("Mint de tokens supplémentaires")
    contract.mint(to_address=admin.address, amount=50_000).run(sender=admin)
    scenario.verify(contract.get_total_supply() > 2_250_000)
    
    # Transfert direct entre utilisateurs
    scenario.h2("Transferts directs")
    contract.transfer(to_address=dave.address, amount=1_000).run(sender=alice)
    scenario.verify(contract.get_balance(dave.address) > 25_000)
    
    # === PHASE 7: TESTS DE SÉCURITÉ ===
    scenario.h1("Phase 7: Tests de sécurité")
    
    # Test: Prix avec trop de décimales (doit échouer)
    scenario.h2("Test prix invalide")
    contract.place_buy_order(price=sp.mutez(1_123_456), quantity=10).run(
        sender=bob, 
        amount=sp.tez(11.23456),
        valid=False,  # Doit échouer
        exception="Prix doit avoir maximum 2 décimales"
    )
    
    # Test: Vente sans solde suffisant (doit échouer)
    scenario.h2("Test solde insuffisant")
    contract.place_sell_order(price=sp.mutez(1_200_000), quantity=1_000_000).run(
        sender=dave,
        valid=False,  # Doit échouer
        exception="Solde insuffisant"
    )
    
    # Test: Mint par non-admin (doit échouer)
    scenario.h2("Test mint non autorisé")
    contract.mint(to_address=bob.address, amount=1000).run(
        sender=bob,
        valid=False,  # Doit échouer
        exception="Seul l'admin peut mint"
    )
    
    # === RÉSULTATS FINAUX ===
    scenario.h1("Résultats finaux")
    
    scenario.h2("Soldes finaux")
    final_alice = contract.get_balance(alice.address)
    final_bob = contract.get_balance(bob.address) 
    final_charlie = contract.get_balance(charlie.address)
    final_dave = contract.get_balance(dave.address)
    final_admin = contract.get_balance(admin.address)
    
    scenario.show(final_alice)
    scenario.show(final_bob)
    scenario.show(final_charlie)
    scenario.show(final_dave)
    scenario.show(final_admin)
    
    # Vérification de conservation des tokens
    total_distributed = final_alice + final_bob + final_charlie + final_dave + final_admin
    scenario.verify(total_distributed == contract.get_total_supply())
    
    scenario.h2("Statistiques finales")
    final_price = contract.get_last_price()
    final_volume = contract.get_volume_24h()
    final_supply = contract.get_total_supply()
    
    scenario.show(final_price)
    scenario.show(final_volume)  
    scenario.show(final_supply)
    
    scenario.h2("Test complet réussi!")

@sp.add_test()
def test_edge_cases():
    """Test des cas limites et des erreurs"""
    
    scenario = sp.test_scenario("Tests des cas limites", main)
    
    # Setup minimal
    admin = sp.test_account("Admin")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    
    contract = main.ActionChainToken(
        admin=admin.address,
        initial_supply=100_000,
        token_name="Test Token",
        token_symbol="TEST"
    )
    scenario += contract
    
    # Distribution
    contract.mint(to_address=alice.address, amount=1_000).run(sender=admin)
    contract.mint(to_address=bob.address, amount=1_000).run(sender=admin)
    
    scenario.h2("Tests des cas limites")
    
    # Test 1: Prix minimum
    contract.place_sell_order(price=sp.mutez(10_000), quantity=1).run(sender=alice)  # 0.01 tez
    contract.place_buy_order(price=sp.mutez(10_000), quantity=1).run(
        sender=bob, amount=sp.mutez(10_000)
    )
    
    # Test 2: Quantité de 1 token
    contract.place_sell_order(price=sp.mutez(1_000_000), quantity=1).run(sender=alice)
    
    # Test 3: Ordre avec montant exact
    contract.place_buy_order(price=sp.mutez(1_000_000), quantity=1).run(
        sender=bob, amount=sp.mutez(1_000_000)
    )
    
    # Test 4: Burn jusqu'à 0
    alice_balance = contract.get_balance(alice.address)
    contract.burn(amount=alice_balance).run(sender=alice)
    scenario.verify(contract.get_balance(alice.address) == 0)
    
    scenario.h2("Cas limites validés")

if __name__ == "__main__":
    # Exécution de tous les tests
    print("Lancement des tests ActionChain Token")
    print("=" * 50)
    
    # Les tests seront exécutés automatiquement par SmartPy
    pass
