from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Account, Transaction
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    account = Account.query.filter_by(user_id=user.id).first()
    return render_template('dashboard.html', user=user, account=account)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        receiver_username = request.form['receiver']
        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            flash('Receiver not found!')
            return redirect(url_for('transfer'))
        
        sender_account = Account.query.filter_by(user_id=session['user_id']).first()
        receiver_account = Account.query.filter_by(user_id=receiver.id).first()

        if sender_account.balance < amount:
            flash('Insufficient balance!')
            return redirect(url_for('transfer'))

        # Perform transaction
        sender_account.balance -= amount
        receiver_account.balance += amount

        txn = Transaction(sender_id=sender_account.id, receiver_id=receiver_account.id, amount=amount)
        db.session.add(txn)
        db.session.commit()

        flash('Transfer Successful!')
        return redirect(url_for('dashboard'))

    return render_template('transfer.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
