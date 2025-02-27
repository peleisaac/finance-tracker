class FinanceTracker:
    def add_transaction(self):
        try:
            print(f"\nAdding a new transaction")
            transaction_type = input("Enter type (income/expense): ").lower()
            if transaction_type not in ["income", "expense"]:
                raise ValueError(
                    "Invalid transaction type. Choose 'income' or 'expense'."
                )
            
            date = input(
                "Enter the date (YYYY-MM-DD) or press enter to ue today's date: "
            )

            amount = float(input("Enter amount: "))

            description = input("Enter description: ")
            category = input("Enter category: ")
            print(f"{date, amount, description, category, transaction_type}")
            print("\nTransaction added successfully!\n")
                
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")
            

