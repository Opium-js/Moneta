from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Transaction, Category
from datetime import datetime, date
from sqlalchemy import extract

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    today = date.today()
    current_month = today.month
    current_year = today.year
    monthly_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).all()
    monthly_income = sum(t.amount for t in monthly_transactions if t.type == 'income')
    monthly_expense = sum(t.amount for t in monthly_transactions if t.type == 'expense')
    monthly_balance = monthly_income - monthly_expense
    expense_by_category = {}
    for t in monthly_transactions:
        if t.type == 'expense':
            cat_name = t.category.name if t.category else 'Other'
            cat_color = t.category.color if t.category else '#95a5a6'
            if cat_name not in expense_by_category:
                expense_by_category[cat_name] = {'amount': 0, 'color': cat_color}
            expense_by_category[cat_name]['amount'] += t.amount
    monthly_data = {'income': [], 'expense': []}
    for month in range(1, current_month + 1):
        month_transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == current_year
        ).all()
        monthly_data['income'].append(
            sum(t.amount for t in month_transactions if t.type == 'income')
        )
        monthly_data['expense'].append(
            sum(t.amount for t in month_transactions if t.type == 'expense')
        )
    recent_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date.desc()).limit(5).all()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    chart_labels = month_names[:current_month]

    return render_template('index.html',
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_balance=monthly_balance,
        expense_by_category=expense_by_category,
        monthly_data=monthly_data,
        chart_labels=chart_labels,
        recent_transactions=recent_transactions,
        current_month=month_names[current_month - 1],
        current_year=current_year
    )