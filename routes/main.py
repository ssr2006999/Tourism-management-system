from flask import render_template, request, session, flash, redirect, url_for
from routes import main_bp
from database import query_db


@main_bp.route('/')
def home():
    popular_packages = query_db("""
        select * from packages order by package_name limit 4
    """, fetch=True)
    return render_template('index.html', popular_packages=popular_packages)


@main_bp.route('/packages')
def packages():
    packages = query_db("select * from packages order by package_name", fetch=True)
    return render_template('packages.html', packages=packages)


@main_bp.route('/package/<int:package_id>')
def package_details(package_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))

    package = query_db("select * from packages where id = %s", (package_id,), fetch=True)

    if not package:
        flash('Package not found.')
        return redirect(url_for('main.packages'))

    package = package[0]
    return render_template('package_details.html', package=package)