from flask import Blueprint, Response, request
from flask_login import login_required, current_user
from app.models import Transaction
import csv
import io
from datetime import datetime

exports_bp = Blueprint('exports', __name__)

@exports_bp.route('/export/csv')
@login_required
def export_csv():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    query = Transaction.query.filter_by(user_id=current_user.id)

    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        )

    transactions = query.order_by(Transaction.date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Date', 'Description', 'Amount', 'Type', 'Category'])
    for t in transactions:
        writer.writerow([
            t.date.strftime('%Y-%m-%d'),
            t.description or '',
            f"{t.amount:.2f}",
            t.type,
            t.category.name if t.category else 'No category'
        ])

    output.seek(0)
    now = datetime.now().strftime('%Y-%m-%d')
    filename = f"moneta-transactions-{now}.csv"
    
    if month and year:
        filename = f"moneta-transactions-{year}-{month:02d}.csv"

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )