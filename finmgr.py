from app import create_app, db
from app.models import User, Account, Transaction, Category, Budget, SavingsGoal, BillReminder, UserSettings

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Account': Account,
        'Transaction': Transaction,
        'Category': Category,
        'Budget': Budget,
        'SavingsGoal': SavingsGoal,
        'BillReminder': BillReminder,
        'UserSettings': UserSettings,
    }

if __name__ == "__main__":
    app.run(debug=True)