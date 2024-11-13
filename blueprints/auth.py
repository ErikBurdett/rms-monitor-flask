from flask import Blueprint, render_template, redirect, url_for, flash, request, session

auth_bp = Blueprint('auth', __name__)

ACCESS_CODE = "hahahahelloworld"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_code = request.form['access_code']
        if entered_code == ACCESS_CODE:
            session['authenticated'] = True
            return redirect(url_for('monitor.index'))
        else:
            flash('Invalid access code. Please try again.')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
