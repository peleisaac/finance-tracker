from finance import FinanceTracker


class MainMenu:
    def __init__(self):
        self.tracker = FinanceTracker()
        
    
    def display_menu(self):
        menu = """
        
        Welcome to your Finance Tracker Application.
        Please select an option below:
        ========================
        
        1. Add Transactions
        
        0. Exit
        ========================
        """
        print(menu)
        
    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")
            if choice == "1":
                self.tracker.add_transaction()
                
            elif choice == "0":
                print("Exiting application. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    mainmenu = MainMenu()
    mainmenu.run()

Main.py

