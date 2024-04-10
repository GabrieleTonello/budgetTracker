from flask import Flask, render_template, flash, request, redirect, url_for, session
from wtforms import Form, StringField, PasswordField, TextAreaField, IntegerField, validators
from wtforms.fields import EmailField
from passlib.hash import sha256_crypt
import sqlite3
import plotly.graph_objects as go
from functools import wraps

app = Flask(__name__)
app.secret_key ="set secret keys"
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 3}


class SignUpForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=100)])
    last_name = StringField('Last Name', [validators.Length(min=1, max=100)])
    email = EmailField('Email address', [
        validators.DataRequired()]) #TODO , validators.Email()
    username = StringField('Username', [validators.Length(min=4, max=100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'logged_in' in session and session['logged_in'] is True:
        flash('You are already logged in', 'info')
        return redirect(url_for('hello_world'))
    form = SignUpForm(request.form)
    try:
        a = form.validate()
        a = 0
    except Exception as e:
        a = e

    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        conn = sqlite3.connect('budget_tracker.db')
        cur = conn.cursor()
        result = cur.execute(f"SELECT * FROM users WHERE email='{email}'")
        result = result.fetchone()
        cur.close()
        if result is not None:
            flash('The entered email address has already been taken.Please try using or creating another one.', 'info')
            return redirect(url_for('signup'))
        else:
            conn = sqlite3.connect('budget_tracker.db')
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO users (first_name, last_name, email, username, password, role) VALUES (?, ?, ?, ?, ?, ?)""",
                (first_name, last_name, email, username, password, "user"))
            conn.commit()
            cur.close()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
    return render_template('signUp.html', form=form)


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in'] == True:
        flash('You are already logged in', 'info')
        return redirect(url_for('hello_world'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_input = form.password.data

        conn = sqlite3.connect('budget_tracker.db')
        cur = conn.cursor()

        result = cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
        data = result.fetchone()
        cur.close()
        if data is not None:
            userID = data[0]
            password = data[5]
            role = data[6]

            if sha256_crypt.verify(password_input, password):
                session['logged_in'] = True
                session['username'] = username
                session['role'] = role
                session['userID'] = userID

                flash('You are now logged in', 'success')
                return redirect(url_for('hello_world'))
            else:
                error = 'Invalid Password'
                return render_template('login.html', form=form, error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', form=form, error=error)

    return render_template('login.html', form=form)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login', 'info')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@is_logged_in
def hello_world():  # put application's code here
    if request.method == 'POST':
        month = f"{int(request.form['month']):02}"
        year = f"{int(request.form['year']):04}"
        # Create cursor
        conn = sqlite3.connect('budget_tracker.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT SUM(amount) FROM transactions  ")

        data = cur.fetchone()
        totalExpenses = f"{data[0] :.1f}"
        query = "SELECT * FROM transactions  ORDER BY date DESC"
        if month != "00":
            query = f"SELECT * FROM transactions WHERE date >= '{year}/{month}/01' AND date <= '{year}/{month}/31' ORDER BY date DESC"

        result = cur.execute(query)
        result = result.fetchall()
        cur.close()
        if len(result) > 0:
            transactions = result
            return render_template('transactionHistory.html', totalExpenses=totalExpenses, transactions=transactions)
        else:
            flash('No Transactions Found', 'success')
            return redirect(url_for('hello_world'))
        # Close connection


    else:
        # Create cursor
        conn = sqlite3.connect('budget_tracker.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT SUM(amount) FROM transactions ")

        data = cur.fetchone()
        totalExpenses = f"{data[0]:.1f}"

        # Get Latest Transactions made by a particular user
        result = cur.execute(
            "SELECT * FROM transactions  ORDER BY date DESC"
        )
        result = result.fetchall()
        cur.close()
        if len(result[0]) > 0:
            transactions = result
            return render_template('transactionHistory.html', totalExpenses=totalExpenses, transactions=transactions)
        else:
            flash('No Transactions Found', 'success')
            return redirect(url_for('hello_world'))
        # Close connection


@app.route('/deleteTransaction/<string:id>', methods=['POST'])
@is_logged_in
def deleteTransaction(id):
    # Create cursor
    conn = sqlite3.connect('budget_tracker.db')
    cur = conn.cursor()

    # Execute
    cur.execute(f"DELETE FROM transactions WHERE id = {id}")

    # Commit to DB
    conn.commit()
    # Close connection
    cur.close()

    flash('Transaction Deleted', 'success')

    return redirect(url_for('hello_world'))

@app.route('/editTransaction/<id>', methods=['POST'])
@is_logged_in
def editTransaction(id):
    # Create cursor
    conn = sqlite3.connect('budget_tracker.db')
    date = request.form.get('date', None)
    date = date.replace("-", "/")
    bank = request.form.get('bank', None)
    amount = request.form.get('amount', None)
    description = request.form.get('description', None)
    category = request.form.get('category', None)

    cur = conn.cursor()
    # Execute
    cur.execute(f"UPDATE transactions SET account = ?, date = ?, description = ?, amount = ?, category = ? WHERE id = ?",
                (bank, date, description, amount, category, id))

    # Commit to DB
    conn.commit()
    # Close connection
    cur.close()
    flash('Transaction Modified', 'success')

    return redirect(url_for('hello_world'))

@app.route('/addTransaction', methods=['POST'])
@is_logged_in
def addTransaction():
    # Create cursor
    conn = sqlite3.connect('budget_tracker.db')
    date = request.form.get('date', None)
    date = date.replace("-", "/")
    bank = request.form.get('bank', None)
    amount = request.form.get('amount', None)
    description = request.form.get('description', None)
    category = request.form.get('category', None)
    cur = conn.cursor()
    # Execute
    cur.execute('''INSERT INTO transactions (account, date, description, amount, category)
                      VALUES (?, ?, ?, ?, ?)''', (bank, date, description, amount, category))

    # Commit to DB
    conn.commit()
    # Close connection
    cur.close()
    flash('Transaction Added', 'success')

    return redirect(url_for('hello_world'))


@app.route('/category')
@is_logged_in
def categoryBarCharts():
    conn = sqlite3.connect('budget_tracker.db')
    cur = conn.cursor()
    result = cur.execute(
        f"SELECT SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS outflow, category FROM transactions GROUP BY category")
    result = result.fetchall()
    if len(result) > 0:
        values = []
        labels = []
        for transaction in result:
            values.append(-transaction[0])
            labels.append(transaction[1])


        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_traces(textinfo='label+value', hoverinfo='percent')
        fig.update_layout(title_text='Spending by category')
        fig.show()
    cur.close()
    return redirect(url_for('hello_world'))


@app.route('/monthly_bar')
@is_logged_in
def monthlyBar():
    conn = sqlite3.connect('budget_tracker.db')
    cur = conn.cursor()
    result = cur.execute(
        f"SELECT  SUM(CASE WHEN amount >= 0 THEN amount ELSE 0 END) AS inflow, SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS outflow, STRFTIME('%Y-%m',  REPLACE(date, '/', '-')) as month FROM transactions GROUP BY STRFTIME('%m-%Y', REPLACE(date, '/', '-')) ORDER BY month")
    result = result.fetchall()
    if len(result) > 0:
        ingress = []
        out = []
        month = []
        for transaction in result:
            ingress.append(transaction[0])
            out.append(transaction[1])
            month.append(transaction[2])

        fig = go.Figure([ go.Bar(x=month, y=ingress, name="ingress"), go.Bar(x=month, y=out, name="out")])
        fig.update_layout(title_text='Monthly Income and Spending')
        fig.show()
    cur.close()
    return redirect(url_for('hello_world'))


@app.route('/monthly_performance')
@is_logged_in
def monthlyPerformance():
    conn = sqlite3.connect('budget_tracker.db')
    cur = conn.cursor()
    result = cur.execute(
        f"SELECT  SUM(amount),  STRFTIME('%Y-%m-%d',  REPLACE(date, '/', '-')) as date FROM transactions GROUP BY STRFTIME('%d-%m-%Y', REPLACE(date, '/', '-')) ORDER BY date")
    result = result.fetchall()
    if len(result) > 0:
        sum = 0
        state = []
        day = []
        for transaction in result:
            sum += int(transaction[0])
            state.append(sum)
            day.append(transaction[1])

        fig = go.Figure([go.Bar(x=day, y=state, name="balance")])
        fig.update_layout(title_text='Monthly Balance')
        fig.show()
    cur.close()
    return redirect(url_for('hello_world'))


@app.route('/outflow')
@is_logged_in
def outflowChart():
    conn = sqlite3.connect('budget_tracker.db')
    cur = conn.cursor()
    result = cur.execute(
        f"SELECT Sum(CASE WHEN amount <= 0 THEN amount ELSE 0 END) AS amount, account FROM transactions GROUP BY account ORDER BY account")
    result = result.fetchall()
    if len(result) > 0:
        transactions = result
        values = []
        labels = []
        for transaction in transactions:
            values.append(-transaction[0])
            labels.append(transaction[1])

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_traces(textinfo='label+value', hoverinfo='percent')
        fig.update_layout(
            title_text='Bank used for paying')
        fig.show()
    cur.close()
    return redirect(url_for('hello_world'))


if __name__ == '__main__':
    app.run(debug=True)
