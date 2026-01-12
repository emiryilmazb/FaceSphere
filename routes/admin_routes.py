from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from extensions import db
from database_models import User, AccessLog

bp = Blueprint('admin', __name__)


@bp.route('/admin_panel')
def admin_panel():
    if 'logged_in' in session and session['logged_in']:
        users = User.query.all()
        unauthorized_logs = AccessLog.query.all()
        return render_template('admin_panel.html', users=users, unauthorized_logs=unauthorized_logs)
    else:
        return redirect(url_for('main.index'))


@bp.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    # TODO: Use environment variables or a more secure method for admin credentials
    if username == 'admin' and password == 'admin':
        session['logged_in'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.index'))


@bp.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        department = request.form.get('department')
        phone_number = request.form.get('phone_number')
        entry_time = request.form.get('entry_time')
        exit_time = request.form.get('exit_time')
        photo_location = request.form.get('photo_location')

        new_user = User(first_name=first_name, last_name=last_name, department=department,
                        phone_number=phone_number, entry_time=entry_time, exit_time=exit_time,
                        photo_location=photo_location)
        db.session.add(new_user)
        db.session.commit()
    return jsonify({'success': True})


@bp.route('/remove_user', methods=['POST'])
def remove_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_to_remove = User.query.get(user_id)
        if user_to_remove:
            db.session.delete(user_to_remove)
            db.session.commit()

    return jsonify({'success': True})
