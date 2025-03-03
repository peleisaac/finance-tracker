class FinanceTracker:
    def load_transactions(self):
        if self.transactions_file.exists():
            with open(self.transactions_file, "r") as file:
                data = json.load(file)
                transactions_data = data.get("transactions", {})

                if isinstance(transactions_data, dict):
                    self.transactions = {
                        "income": [
                            Transaction.from_dict(t)
                            for t in transactions_data.get("income", [])
                        ],
                        "expense": [
                            Transaction.from_dict(t)
                            for t in transactions_data.get("expense", [])
                        ],
                    }
                else:
                    self.transactions = {"income": [], "expense": []}
                    print("Warning: Invalid transactions format. Resetting to default.")

                self.budgets = data.get("budgets", {})

                if not isinstance(self.budgets, dict):
                    self.budgets = {}
                    print("Warning: Invalid budgets format. Resetting to default.")
        else:
            self.save_transactions()

    def save_transactions(self):
        data = {
            "transactions": {
                "income": [t.to_dict() for t in self.transactions["income"]],
                "expense": [t.to_dict() for t in self.transactions["expense"]],
            },
            "budgets": self.budgets,
        }
        with open(self.transactions_file, "w") as file:
            json.dump(data, file, indent=4)

    def add_transaction(self):
        try:
            print(f"\nAdding a new transaction for {self.username}...")
            transaction_type = input("Enter type (income/expense): ").lower()
            if transaction_type not in ["income", "expense"]:
                raise ValueError(
                    "Invalid transaction type. Choose 'income' or 'expense'."
                )
            
            date_str = input(
                "Enter the date (YYYY-MM-DD) or press enter to ue today's date: "
            )
            if not date_str:
                date = datetime.date.today()
            else:
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if date > datetime.date.today():
                        print(
                            "Warning: You are adding a transaction with a future date!"
                        )
                except ValueError:
                    print("Invalid date format: please YYYY-MM-DD")
                    return

            amount = float(input("Enter amount: "))
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
            
            if transaction_type == "expense" and amount > self.get_balance():
                print("\n⚠️ Warning: Insufficient balance! Transaction not added.\n")
                return

            description = input("Enter description: ")
            category = (
                Category.auto_categorize(description)
                if transaction_type == "expense" 
                else "Salary"
            )

            new_transaction = Transaction(
                date, amount, category, description, transaction_type
            )
            if new_transaction in self.transactions[transaction_type]:
                print("Transaction already exists! \n")
                return

            self.transactions[transaction_type].append(new_transaction)
            self.save_transactions()

            # Real-time budget alert
            if transaction_type == "expense" and category in self.budgets:
                spent = sum(
                    t.amount
                    for t in self.transactions["expense"]
                    if t.category == category
                )
                if spent > self.budgets[category]:
                    print(
                        f"\n⚠️ Warning: You have exceeded your budget for {category}!\n"
                    )

            print("\nTransaction added successfully!\n")
            
            balance = self.get_balance()
            if balance < 100:
                print(f"⚠️ Warning: Your balance is low! Remaining: ${balance}")
                
        except ValueError as e:
            print(f"\nInput Error: {e}\n")
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")
