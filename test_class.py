class consulting:
    def __init__(self, client, project, budget):
        self.client = client        # remember WHO owns this account
        self.project = project    # remember HOW MUCH money
        self.budget = budget

    def expense(self, budget):
        self.budget -= budget

    def show_balance(self):
        print(f"{self.client} has budget remaining ${self.budget} for project {self.project}")

account = consulting("Walmart", "Promo code", 10000)
account.expense(500)
account.show_balance()

