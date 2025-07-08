import smartpy as sp

@sp.module
def main():
    # Types de donnees pour le token par actions
    t_order: type = sp.record(
        trader=sp.address,
        order_type=sp.string,  # "buy" ou "sell"
        price=sp.mutez,        # Prix en mutez
        quantity=sp.nat,       # Quantite de tokens
        timestamp=sp.timestamp
    )
    
    t_trade: type = sp.record(
        buyer=sp.address,
        seller=sp.address,
        price=sp.mutez,
        quantity=sp.nat,
        timestamp=sp.timestamp
    )

    class ActionChainToken(sp.Contract):
        def __init__(self, admin, initial_supply, token_name, token_symbol):
            # Initialisation du storage
            self.data = sp.record(
                # Token standard
                balances=sp.big_map({admin: initial_supply}),
                total_supply=initial_supply,
                admin=admin,
                
                # Systeme d'ordres
                buy_orders=sp.big_map(),
                sell_orders=sp.big_map(),
                order_counter=0,
                
                # Historique des trades
                trades=sp.big_map(),
                trade_counter=0,
                
                # Statistiques
                last_price=sp.mutez(1000000),  # Prix initial 1.00 tez
                volume_24h=0,
                last_volume_reset=sp.now,
                
                # Configuration
                token_name=token_name,
                token_symbol=token_symbol,
                decimals=6
            )

        @sp.entrypoint
        def place_buy_order(self, price, quantity):
            """Place un ordre d'achat"""
            assert sp.amount == sp.split_tokens(price, quantity, 1), "Montant incorrect"
            assert quantity > 0, "Quantite doit etre positive"
            assert price > sp.mutez(0), "Prix doit etre positif"
            
            # Creer l'ordre
            order = sp.record(
                trader=sp.sender,
                order_type="buy",
                price=price,
                quantity=quantity,
                timestamp=sp.now
            )
            
            self.data.buy_orders[self.data.order_counter] = order
            self.data.order_counter += 1

        @sp.entrypoint
        def place_sell_order(self, price, quantity):
            """Place un ordre de vente"""
            assert sp.amount == sp.tez(0), "Pas de transfert autorise"
            assert quantity > 0, "Quantite doit etre positive"
            assert price > sp.mutez(0), "Prix doit etre positif"
            
            # Verifier que le vendeur a assez de tokens
            seller_balance = self.data.balances.get(sp.sender, default=0)
            assert seller_balance >= quantity, "Solde insuffisant"
            
            # Creer l'ordre
            order = sp.record(
                trader=sp.sender,
                order_type="sell",
                price=price,
                quantity=quantity,
                timestamp=sp.now
            )
            
            self.data.sell_orders[self.data.order_counter] = order
            self.data.order_counter += 1

        @sp.entrypoint
        def execute_trade(self, buy_order_id, sell_order_id):
            """Execute un trade entre deux ordres specifiques"""
            assert self.data.buy_orders.contains(buy_order_id), "Ordre d'achat introuvable"
            assert self.data.sell_orders.contains(sell_order_id), "Ordre de vente introuvable"
            
            buy_order = self.data.buy_orders[buy_order_id]
            sell_order = self.data.sell_orders[sell_order_id]
            
            # Verifier que les prix sont compatibles
            assert buy_order.price >= sell_order.price, "Prix incompatibles"
            
            # Verifier les soldes
            seller_balance = self.data.balances.get(sell_order.trader, default=0)
            assert seller_balance >= sell_order.quantity, "Vendeur n'a pas assez de tokens"
            
            # Calculer la quantite a echanger
            trade_quantity = sp.min(buy_order.quantity, sell_order.quantity)
            trade_price = sell_order.price  # Prix du vendeur
            
            # Mettre a jour les soldes
            buyer_balance = self.data.balances.get(buy_order.trader, default=0)
            new_seller_balance = sp.as_nat(seller_balance - trade_quantity)
            
            if new_seller_balance == 0:
                if self.data.balances.contains(sell_order.trader):
                    del self.data.balances[sell_order.trader]
            else:
                self.data.balances[sell_order.trader] = new_seller_balance
                
            self.data.balances[buy_order.trader] = buyer_balance + trade_quantity
            
            # Transferer les tez
            total_amount = sp.split_tokens(trade_price, trade_quantity, 1)
            sp.send(sell_order.trader, total_amount)
            
            # Enregistrer le trade
            trade = sp.record(
                buyer=buy_order.trader,
                seller=sell_order.trader,
                price=trade_price,
                quantity=trade_quantity,
                timestamp=sp.now
            )
            self.data.trades[self.data.trade_counter] = trade
            self.data.trade_counter += 1
            
            # Mettre a jour les statistiques
            self.data.last_price = trade_price
            self.data.volume_24h += trade_quantity
            
            # Mettre a jour ou supprimer les ordres
            if buy_order.quantity == trade_quantity:
                del self.data.buy_orders[buy_order_id]
            else:
                new_buy_quantity = sp.as_nat(buy_order.quantity - trade_quantity)
                self.data.buy_orders[buy_order_id] = sp.record(
                    trader=buy_order.trader,
                    order_type=buy_order.order_type,
                    price=buy_order.price,
                    quantity=new_buy_quantity,
                    timestamp=buy_order.timestamp
                )
            
            if sell_order.quantity == trade_quantity:
                del self.data.sell_orders[sell_order_id]
            else:
                new_sell_quantity = sp.as_nat(sell_order.quantity - trade_quantity)
                self.data.sell_orders[sell_order_id] = sp.record(
                    trader=sell_order.trader,
                    order_type=sell_order.order_type,
                    price=sell_order.price,
                    quantity=new_sell_quantity,
                    timestamp=sell_order.timestamp
                )

        @sp.entrypoint
        def cancel_order(self, order_id, order_type):
            """Annule un ordre"""
            if order_type == "buy":
                assert self.data.buy_orders.contains(order_id), "Ordre introuvable"
                order = self.data.buy_orders[order_id]
                assert order.trader == sp.sender, "Pas autorise"
                
                # Rembourser l'acheteur
                refund_amount = sp.split_tokens(order.price, order.quantity, 1)
                sp.send(sp.sender, refund_amount)
                
                del self.data.buy_orders[order_id]
                
            else:  # sell
                assert self.data.sell_orders.contains(order_id), "Ordre introuvable"
                order = self.data.sell_orders[order_id]
                assert order.trader == sp.sender, "Pas autorise"
                
                del self.data.sell_orders[order_id]

        @sp.entrypoint
        def transfer(self, to_address, amount):
            """Transfere des tokens"""
            assert sp.amount == sp.tez(0), "Pas de transfert autorise"
            
            sender_balance = self.data.balances.get(sp.sender, default=0)
            assert sender_balance >= amount, "Solde insuffisant"
            
            receiver_balance = self.data.balances.get(to_address, default=0)
            
            # Mettre a jour les soldes
            new_sender_balance = sp.as_nat(sender_balance - amount)
            if new_sender_balance == 0:
                if self.data.balances.contains(sp.sender):
                    del self.data.balances[sp.sender]
            else:
                self.data.balances[sp.sender] = new_sender_balance
                
            self.data.balances[to_address] = receiver_balance + amount

        @sp.entrypoint
        def mint(self, to_address, amount):
            """Mint de nouveaux tokens (admin seulement)"""
            assert sp.sender == self.data.admin, "Seul l'admin peut mint"
            assert sp.amount == sp.tez(0), "Pas de transfert autorise"
            
            receiver_balance = self.data.balances.get(to_address, default=0)
            self.data.balances[to_address] = receiver_balance + amount
            self.data.total_supply += amount

        @sp.entrypoint
        def burn(self, amount):
            """Burn des tokens"""
            assert sp.amount == sp.tez(0), "Pas de transfert autorise"
            
            sender_balance = self.data.balances.get(sp.sender, default=0)
            assert sender_balance >= amount, "Solde insuffisant"
            
            new_sender_balance = sp.as_nat(sender_balance - amount)
            if new_sender_balance == 0:
                if self.data.balances.contains(sp.sender):
                    del self.data.balances[sp.sender]
            else:
                self.data.balances[sp.sender] = new_sender_balance
            new_total_supply = sp.as_nat(self.data.total_supply - amount)
            self.data.total_supply = new_total_supply

        # Vues pour lire les donnees
        @sp.onchain_view()
        def get_balance(self, address):
            return self.data.balances.get(address, default=0)

        @sp.onchain_view()
        def get_total_supply(self):
            return self.data.total_supply

        @sp.onchain_view()
        def get_last_price(self):
            return self.data.last_price

        @sp.onchain_view()
        def get_volume_24h(self):
            return self.data.volume_24h

# Tests
@sp.add_test()
def test_actionchain_token():
    scenario = sp.test_scenario("ActionChain Token Test", main)
    
    # Comptes de test
    admin = sp.test_account("Admin")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    
    # Deployer le contrat
    token = main.ActionChainToken(
        admin=admin.address,
        initial_supply=1000000,  # 1M tokens
        token_name="ActionChain Token",
        token_symbol="ACT"
    )
    scenario += token
    
    # Test 1: Mint des tokens pour Alice et Bob
    scenario.h2("Mint tokens")
    token.mint(to_address=alice.address, amount=10000).run(sender=admin)
    token.mint(to_address=bob.address, amount=10000).run(sender=admin)
    
    # Test 2: Alice place un ordre de vente
    scenario.h2("Alice place un ordre de vente")
    token.place_sell_order(price=sp.mutez(1200000), quantity=100).run(sender=alice)  # 1.20 tez par token
    
    # Test 3: Bob place un ordre d'achat
    scenario.h2("Bob place un ordre d'achat")
    token.place_buy_order(price=sp.mutez(1200000), quantity=50).run(
        sender=bob, 
        amount=sp.tez(60)  # 50 * 1.20 = 60 tez
    )
    
    # Test 4: Execution manuelle du trade
    scenario.h2("Execution du trade")
    token.execute_trade(buy_order_id=1, sell_order_id=0).run(sender=admin)
    
    # Test 5: Verifier les soldes apres le trade
    scenario.h2("Verification des soldes")
    scenario.verify(token.get_balance(alice.address) == 9950)  # 10000 - 50
    scenario.verify(token.get_balance(bob.address) == 10050)   # 10000 + 50
    
    # Test 6: Annulation d'ordre
    scenario.h2("Test d'annulation d'ordre")
    token.place_buy_order(price=sp.mutez(1100000), quantity=10).run(
        sender=bob,
        amount=sp.tez(11)
    )
    
    # Annuler l'ordre (il devrait y avoir un remboursement)
    token.cancel_order(order_id=2, order_type="buy").run(sender=bob)

    scenario.h2("Tests termines avec succes!")
