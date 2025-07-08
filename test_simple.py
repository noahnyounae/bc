import smartpy as sp

@sp.module
def main():
    class SimpleToken(sp.Contract):
        def __init__(self, admin):
            self.data = sp.record(
                admin=admin,
                balances=sp.big_map({admin: 1000})
            )
        
        @sp.entrypoint
        def mint(self, to_address, amount):
            # assert sp.sender == self.data.admin, "Only admin can mint"
            balance = self.data.balances.get(to_address, default=0)
            self.data.balances[to_address] = balance + amount

@sp.add_test()
def test_simple():
    scenario = sp.test_scenario("Simple Test", main)
    admin = sp.test_account("Admin")
    alice = sp.test_account("Alice")
    
    token = main.SimpleToken(admin=admin.address)
    scenario += token
    
    scenario.h2("Minting tokens")
    scenario += token.mint(to_address=alice.address, amount=100).run(sender=admin)

if __name__ == "__main__":
    main.SimpleToken.compiler_version = "0.22.0"
