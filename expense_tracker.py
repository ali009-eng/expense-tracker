#!/usr/bin/env python3

import json
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import sys

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ExpenseTracker:
    def __init__(self, data_file='expenses.json'):
        self.data_file = data_file
        self.expenses = []
        self.categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Shopping', 'Health', 'Other']
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.expenses = json.load(f)
                print(f"Loaded {len(self.expenses)} expenses from {self.data_file}")
            except (json.JSONDecodeError, FileNotFoundError):
                print("Could not load data file. Starting fresh.")
                self.expenses = []
        else:
            print("Starting with a new expense tracker.")
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.expenses, f, indent=2)
            print(f"Data saved to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_expense(self):
        print("\nAdd New Expense")
        print("-" * 30)
        
        while True:
            try:
                amount = float(input("Enter amount: $"))
                if amount <= 0:
                    print("Amount must be positive. Try again.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        print("\nAvailable categories:")
        for i, category in enumerate(self.categories, 1):
            print(f"  {i}. {category}")
        
        while True:
            try:
                choice = input(f"\nSelect category (1-{len(self.categories)}) or enter custom: ")
                
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(self.categories):
                        category = self.categories[index]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(self.categories)}")
                else:
                    category = choice.strip().title()
                    if category:
                        if category not in self.categories:
                            self.categories.append(category)
                        break
                    else:
                        print("Category cannot be empty.")
            except ValueError:
                print("Invalid input. Try again.")
        
        date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_input:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                date = date_input
            except ValueError:
                print("Invalid date format. Using today's date.")
                date = datetime.now().strftime("%Y-%m-%d")
        
        description = input("Description (optional): ").strip()
        
        expense = {
            'amount': amount,
            'category': category,
            'date': date,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        
        self.expenses.append(expense)
        print(f"\nAdded expense: ${amount:.2f} for {category} on {date}")
        self.save_data()
    
    def view_expenses(self):
        if not self.expenses:
            print("\nNo expenses recorded yet.")
            return
        
        print("\nView Expenses")
        print("-" * 30)
        print("1. View all expenses")
        print("2. Filter by category")
        print("3. Filter by date range")
        print("4. Filter by month")
        
        choice = input("\nSelect option (1-4): ")
        
        filtered_expenses = self.expenses.copy()
        
        if choice == '2':
            print("\nAvailable categories:")
            categories_in_data = list(set(exp['category'] for exp in self.expenses))
            for i, cat in enumerate(categories_in_data, 1):
                print(f"  {i}. {cat}")
            
            try:
                cat_choice = int(input("Select category: ")) - 1
                selected_category = categories_in_data[cat_choice]
                filtered_expenses = [exp for exp in self.expenses if exp['category'] == selected_category]
            except (ValueError, IndexError):
                print("Invalid selection. Showing all expenses.")
        
        elif choice == '3':
            start_date = input("Start date (YYYY-MM-DD): ")
            end_date = input("End date (YYYY-MM-DD): ")
            try:
                filtered_expenses = [
                    exp for exp in self.expenses 
                    if start_date <= exp['date'] <= end_date
                ]
            except:
                print("Invalid date range. Showing all expenses.")
        
        elif choice == '4':
            month = input("Enter month (YYYY-MM): ")
            try:
                filtered_expenses = [
                    exp for exp in self.expenses 
                    if exp['date'].startswith(month)
                ]
            except:
                print("Invalid month format. Showing all expenses.")
        
        self.display_expenses_table(filtered_expenses)
    
    def display_expenses_table(self, expenses):
        if not expenses:
            print("\nNo expenses found for the selected criteria.")
            return
        
        print(f"\nFound {len(expenses)} expense(s)")
        print("-" * 70)
        print(f"{'Date':<12} {'Category':<15} {'Amount':<10} {'Description':<25}")
        print("-" * 70)
        
        total = 0
        for expense in sorted(expenses, key=lambda x: x['date']):
            desc = expense['description'][:22] + "..." if len(expense['description']) > 25 else expense['description']
            print(f"{expense['date']:<12} {expense['category']:<15} ${expense['amount']:<9.2f} {desc:<25}")
            total += expense['amount']
        
        print("-" * 70)
        print(f"{'Total:':<37} ${total:.2f}")
    
    def calculate_totals(self):
        if not self.expenses:
            print("\nNo expenses recorded yet.")
            return
        
        print("\nCalculate Totals")
        print("-" * 30)
        print("1. Monthly total")
        print("2. Weekly total")
        print("3. Category breakdown")
        print("4. All-time total")
        
        choice = input("Select option (1-4): ")
        
        if choice == '1':
            self.get_monthly_total()
        elif choice == '2':
            self.get_weekly_total()
        elif choice == '3':
            self.show_category_breakdown()
        elif choice == '4':
            total = sum(exp['amount'] for exp in self.expenses)
            print(f"\nAll-time total: ${total:.2f}")
    
    def get_monthly_total(self):
        month = input("\nEnter month (YYYY-MM) or press Enter for current month: ").strip()
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        monthly_expenses = [exp for exp in self.expenses if exp['date'].startswith(month)]
        total = sum(exp['amount'] for exp in monthly_expenses)
        
        print(f"\nTotal for {month}: ${total:.2f}")
        print(f"Number of transactions: {len(monthly_expenses)}")
    
    def get_weekly_total(self):
        today = datetime.now()
        week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        
        weekly_expenses = [
            exp for exp in self.expenses 
            if week_ago <= exp['date'] <= today_str
        ]
        total = sum(exp['amount'] for exp in weekly_expenses)
        
        print(f"\nTotal for last 7 days: ${total:.2f}")
        print(f"Number of transactions: {len(weekly_expenses)}")
    
    def show_category_breakdown(self):
        category_totals = defaultdict(float)
        for expense in self.expenses:
            category_totals[expense['category']] += expense['amount']
        
        if not category_totals:
            print("\nNo expenses to analyze.")
            return
        
        print("\nSpending by Category")
        print("-" * 40)
        
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        total_spending = sum(category_totals.values())
        
        for category, amount in sorted_categories:
            percentage = (amount / total_spending) * 100
            print(f"{category:<20} ${amount:>8.2f} ({percentage:>5.1f}%)")
        
        print("-" * 40)
        print(f"{'Total':<20} ${total_spending:>8.2f} (100.0%)")
    
    def export_csv(self):
        if not self.expenses:
            print("\nNo expenses to export.")
            return
        
        filename = input("Enter CSV filename (or press Enter for 'expenses.csv'): ").strip()
        if not filename:
            filename = 'expenses.csv'
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['date', 'category', 'amount', 'description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for expense in self.expenses:
                    writer.writerow({
                        'date': expense['date'],
                        'category': expense['category'],
                        'amount': expense['amount'],
                        'description': expense['description']
                    })
            
            print(f"Exported {len(self.expenses)} expenses to {filename}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def plot_chart(self):
        if not HAS_MATPLOTLIB:
            print("Matplotlib not installed. Install it with: pip install matplotlib")
            return
        
        if not self.expenses:
            print("\nNo expenses to visualize.")
            return
        
        category_totals = defaultdict(float)
        for expense in self.expenses:
            category_totals[expense['category']] += expense['amount']
        
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, amounts, color='lightblue', edgecolor='darkblue', alpha=0.8)
        
        plt.title('Expenses by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Categories')
        plt.ylabel('Amount ($)')
        plt.xticks(rotation=45, ha='right')
        
        for bar, amount in zip(bars, amounts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.01,
                    f'${amount:.2f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.grid(axis='y', alpha=0.3)
        plt.show()
        print("Chart displayed!")
    
    def show_menu(self):
        print("\n" + "="*40)
        print("EXPENSE TRACKER")
        print("="*40)
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Calculate Totals")
        print("4. Category Breakdown")
        print("5. Export to CSV")
        if HAS_MATPLOTLIB:
            print("6. Plot Chart")
            print("7. Exit")
        else:
            print("6. Exit")
        print("-" * 40)
    
    def run(self):
        print("Welcome to Expense Tracker!")
        
        while True:
            self.show_menu()
            
            max_option = 7 if HAS_MATPLOTLIB else 6
            choice = input(f"Select option (1-{max_option}): ").strip()
            
            if choice == '1':
                self.add_expense()
            elif choice == '2':
                self.view_expenses()
            elif choice == '3':
                self.calculate_totals()
            elif choice == '4':
                self.show_category_breakdown()
            elif choice == '5':
                self.export_csv()
            elif choice == '6' and HAS_MATPLOTLIB:
                self.plot_chart()
            elif choice == str(max_option):
                print("\nThanks for using Expense Tracker!")
                self.save_data()
                break
            else:
                print("Invalid option. Please try again.")

def main():
    tracker = ExpenseTracker()
    try:
        tracker.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! Your data has been saved.")
        tracker.save_data()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Your data has been saved.")
        tracker.save_data()

if __name__ == "__main__":
    main()