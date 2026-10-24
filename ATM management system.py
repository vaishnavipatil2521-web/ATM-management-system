
import json
import os
import hashlib
from datetime import datetime

DATA_FILE = "atm_data.json"


# ---------- Data Management ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"accounts": {}}

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read account data.")
        return {"accounts": {}}


def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


data = load_data()


def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def get_amount(message):
    try:
        amount = float(input(message))
        if not amount > 0 or not amount < float("inf"):
            print("Enter a valid positive amount.")
            return None
        return round(amount, 2)
    except ValueError:
        print("Please enter a valid number.")
        return None


def get_new_pin():
    pin = input("Set a 4-digit ATM PIN: ").strip()
    if len(pin) == 4 and pin.isdigit():
        return pin
    print("PIN must contain exactly 4 digits.")
    return None


# ---------- Account Operations ----------

def create_account():
    print("\n--- Create New Account ---")
    name = input("Enter account holder name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    pin = get_new_pin()
    if pin is None:
        return

    # Generate a unique six-digit account number
    account_no = str(
        next(
            (n for n in range(100001, 1000000)
             if str(n) not in data["accounts"]),
            None
        )
    )

    if account_no == "None":
        print("No account numbers available.")
        return

    data["accounts"][account_no] = {
        "name": name,
        "pin": hash_pin(pin),
        "balance": 0.0,
        "history": []
    }

    save_data()
    print("Account created successfully!")
    print("Your account number is:", account_no)
    print("Please remember your account number and PIN.")


def record_transaction(account, transaction_type, amount, details=""):
    account["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": transaction_type,
        "amount": round(amount, 2),
        "details": details,
        "balance": round(account["balance"], 2)
    })


def check_balance(account):
    print(f"\nAccount Holder: {account['name']}")
    print(f"Available Balance: Rs. {account['balance']:.2f}")


def deposit(account):
    print("\n--- Deposit Money ---")
    amount = get_amount("Enter deposit amount (Rs.): ")

    if amount is None:
        return

    account["balance"] = round(account["balance"] + amount, 2)
    record_transaction(account, "Deposit", amount)
    save_data()
    print(f"Rs. {amount:.2f} deposited successfully.")


def withdraw(account):
    print("\n--- Withdraw Money ---")
    amount = get_amount("Enter withdrawal amount (Rs.): ")

    if amount is None:
        return

    if amount > account["balance"]:
        print("Insufficient balance.")
        return

    account["balance"] = round(account["balance"] - amount, 2)
    record_transaction(account, "Withdrawal", amount)
    save_data()
    print(f"Please collect Rs. {amount:.2f}.")


def transfer_money(account, account_no):
    print("\n--- Transfer Money ---")

    receiver = data["accounts"].get(account_no)

    if receiver is None:
        print("Receiver account not found.")
        return

    amount = get_amount("Enter transfer amount (Rs.): ")
    if amount is None:
        return

    if amount > account["balance"]:
        print("Insufficient balance.")
        return

    if receiver is account:
        print("You cannot transfer money to the same account.")
        return

    account["balance"] = round(account["balance"] - amount, 2)
    receiver["balance"] = round(receiver["balance"] + amount, 2)

    record_transaction(account, "Transfer Sent", amount,
                       f"To account {account_no}")
    record_transaction(receiver, "Transfer Received", amount,
                       "From another account")

    save_data()
    print("Money transferred successfully.")


def transaction_history(account):
    print("\n--- Transaction History ---")
    history = account["history"]

    if not history:
        print("No transactions found.")
        return

    for item in reversed(history):
        print("-" * 40)
        print("Date:", item["date"])
        print("Type:", item["type"])
        print("Amount: Rs.", f"{item['amount']:.2f}")
        if item["details"]:
            print("Details:", item["details"])
        print("Balance: Rs.", f"{item['balance']:.2f}")


def change_pin(account):
    print("\n--- Change ATM PIN ---")
    old_pin = input("Enter current PIN: ").strip()

    if hash_pin(old_pin) != account["pin"]:
        print("Incorrect current PIN.")
        return

    new_pin = get_new_pin()
    if new_pin is None:
        return

    if hash_pin(new_pin) == account["pin"]:
        print("New PIN must be different from the old PIN.")
        return

    account["pin"] = hash_pin(new_pin)
    save_data()
    print("PIN changed successfully.")


# ---------- ATM Menu ----------

def atm_menu(account, account_no):
    while True:
        print("\n========== ATM MENU ==========")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Transaction History")
        print("6. Change PIN")
        print("7. Logout")
        print("==============================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            check_balance(account)
        elif choice == "2":
            deposit(account)
        elif choice == "3":
            withdraw(account)
        elif choice == "4":
            receiver_no = input("Enter receiver account number: ").strip()
            transfer_money(account, receiver_no)
        elif choice == "5":
            transaction_history(account)
        elif choice == "6":
            change_pin(account)
        elif choice == "7":
            print("Logged out successfully.")
            break
        else:
            print("Invalid choice. Please try again.")


def login():
    print("\n--- ATM Login ---")
    account_no = input("Enter account number: ").strip()

    account = data["accounts"].get(account_no)

    if account is None:
        print("Account not found.")
        return

    pin = input("Enter your 4-digit PIN: ").strip()

    if hash_pin(pin) != account["pin"]:
        print("Incorrect PIN.")
        return

    print(f"\nWelcome, {account['name']}!")
    atm_menu(account, account_no)


# ---------- Main Program ----------

def main():
    while True:
        print("\n================================")
        print("     ATM MANAGEMENT SYSTEM")
        print("================================")
        print("1. Create New Account")
        print("2. Login to ATM")
        print("3. Exit")
        print("================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Thank you for using our ATM system.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
