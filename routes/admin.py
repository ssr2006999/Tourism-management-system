from flask import render_template, request, redirect, url_for, session, flash
from routes import admin_bp
from database import query_db
from routes.utils import validate_csrf_token


@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.home'))

    edit_pkg_id = request.args.get('edit_pkg')
    edit_package = None
    if edit_pkg_id:
        edit_package = query_db("select * from packages where id = %s", (edit_pkg_id,), fetch=True)
        edit_package = edit_package[0] if edit_package else None

    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid form submission. Please try again.')
            return redirect(url_for('admin.admin_dashboard'))

        action = request.form.get('action')

        if action == 'add_package':
            package_name = request.form.get('pkg_name', '')
            destination_name = request.form.get('dest_name', '')
            location = request.form.get('dest_location', '')
            days = request.form.get('days', '')
            price = request.form.get('price', '')
            description = request.form.get('description', '')

            if not package_name or not destination_name or not location or not days or not price:
                flash('All fields are required.')
                return redirect(url_for('admin.admin_dashboard'))

            try:
                days = int(days)
                price = float(price)
            except ValueError:
                flash('Invalid days or price format.')
                return redirect(url_for('admin.admin_dashboard'))

            query_db(
                "insert into packages (package_name, destination_name, location, days, price, description) values (%s, %s, %s, %s, %s, %s)",
                (package_name, destination_name, location, days, price, description)
            )
            flash('Package added successfully.')
            return redirect(url_for('admin.admin_dashboard'))

        elif action == 'edit_package':
            pkg_id = request.form.get('pkg_id')
            package_name = request.form.get('pkg_name', '')
            destination_name = request.form.get('dest_name', '')
            location = request.form.get('dest_location', '')
            days = request.form.get('days', '')
            price = request.form.get('price', '')
            description = request.form.get('description', '')

            if not package_name or not destination_name or not location or not days or not price:
                flash('All fields are required.')
                return redirect(url_for('admin.admin_dashboard'))

            try:
                days = int(days)
                price = float(price)
            except ValueError:
                flash('Invalid days or price format.')
                return redirect(url_for('admin.admin_dashboard'))

            query_db(
                "update packages set package_name = %s, destination_name = %s, location = %s, days = %s, price = %s, description = %s where id = %s",
                (package_name, destination_name, location, days, price, description, pkg_id)
            )
            flash('Package updated successfully.')
            return redirect(url_for('admin.admin_dashboard'))

        elif action == 'delete_package':
            pkg_id = request.form.get('pkg_id')

            bookings = query_db(
                "select count(*) as count from bookings where package_id = %s",
                (pkg_id,),
                fetch=True
            )

            if bookings and bookings[0]['count'] > 0:
                flash('Cannot delete package. Bookings are associated with this package.')
            else:
                query_db("delete from packages where id = %s", (pkg_id,))
                flash('Package deleted successfully.')
            return redirect(url_for('admin.admin_dashboard'))

    tourists = query_db("select count(*) as count from users where role = 'user'", fetch=True)
    tourists_count = tourists[0]['count'] if tourists else 0

    packages_count = query_db("select count(*) as count from packages", fetch=True)
    packages_count = packages_count[0]['count'] if packages_count else 0

    bookings_count = query_db("select count(*) as count from bookings", fetch=True)
    bookings_count = bookings_count[0]['count'] if bookings_count else 0

    all_packages = query_db("select * from packages order by package_name", fetch=True)

    all_bookings = query_db("""
        select b.*, u.name as tourist_name, p.package_name, p.destination_name, p.location
        from bookings b
        join users u on b.user_id = u.id
        join packages p on b.package_id = p.id
        order by b.id desc
    """, fetch=True)

    return render_template('admin.html',
                         tourists_count=tourists_count,
                         packages_count=packages_count,
                         bookings_count=bookings_count,
                         all_packages=all_packages,
                         all_bookings=all_bookings,
                         edit_package=edit_package)