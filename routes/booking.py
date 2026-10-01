from datetime import datetime, date
from flask import render_template, request, redirect, url_for, session, flash
from routes import booking_bp
from database import query_db, get_db
from routes.utils import validate_csrf_token


def _get_booking_detail(booking_id, user_id):
    """Get booking details with package and user info."""
    return query_db("""
        select b.*, u.name as tourist_name, p.package_name, p.destination_name, p.location, p.price as package_price
        from bookings b
        join users u on b.user_id = u.id
        join packages p on b.package_id = p.id
        where b.id = %s and b.user_id = %s
    """, (booking_id, user_id), fetch=True)


@booking_bp.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        package_id = request.args.get('package_id')
        next_url = url_for('booking.book', package_id=package_id) if package_id else url_for('main.home')
        return redirect(url_for('auth.login', next=next_url))

    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid form submission. Please try again.')
            return redirect(url_for('booking.book'))

        package_id = request.form.get('package_id')
        travel_date = request.form.get('travel_date')
        num_people = request.form.get('num_people')

        pkg = query_db("select * from packages where id = %s", (package_id,), fetch=True)
        if not pkg:
            flash('Invalid package selected.')
            return redirect(url_for('booking.book'))
        pkg = pkg[0]

        if not travel_date:
            flash('Travel date is required.')
            return redirect(url_for('booking.book'))

        try:
            travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
            if travel_date_obj < date.today():
                flash('Travel date cannot be in the past.')
                return redirect(url_for('booking.book'))
        except ValueError:
            flash('Invalid travel date format.')
            return redirect(url_for('booking.book'))

        try:
            num_people = int(num_people)
            if num_people <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            flash('Number of people must be a positive integer.')
            return redirect(url_for('booking.book'))

        total_price = pkg['price'] * num_people

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """insert into bookings (user_id, package_id, travel_date, num_people, total_price, status, payment_status, payment_method)
                   values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (session['user_id'], package_id, travel_date, num_people, total_price, 'pending', 'pending', None)
            )
            conn.commit()
            booking_id = cursor.lastrowid
        except Exception:
            conn.rollback()
            flash('Error creating booking.')
            return redirect(url_for('booking.book'))
        finally:
            cursor.close()
            conn.close()

        if booking_id:
            return redirect(url_for('booking.payment', booking_id=booking_id))
        else:
            flash('Error creating booking.')
            return redirect(url_for('booking.book'))

    packages = query_db("select * from packages order by package_name", fetch=True)
    selected_package = None
    package_id = request.args.get('package_id')
    if package_id:
        selected_package = query_db("select * from packages where id = %s", (package_id,), fetch=True)
        if selected_package:
            selected_package = selected_package[0]

    return render_template('book.html', packages=packages, selected_package=selected_package)


@booking_bp.route('/booking/confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    booking = _get_booking_detail(booking_id, session['user_id'])

    if not booking:
        flash('Booking not found.')
        return redirect(url_for('booking.my_bookings'))

    booking = booking[0]
    return render_template('booking_confirmation.html', booking=booking)


@booking_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))

    booking = _get_booking_detail(booking_id, session['user_id'])

    if not booking:
        flash('Booking not found.')
        return redirect(url_for('booking.my_bookings'))

    booking = booking[0]

    if booking['payment_status'] == 'completed':
        flash('This booking has already been paid.')
        return redirect(url_for('booking.booking_confirmation', booking_id=booking_id))

    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid form submission. Please try again.')
            return redirect(url_for('booking.payment', booking_id=booking_id))

        payment_method = request.form.get('payment_method')

        if not payment_method or payment_method not in ['UPI', 'Card', 'Cash']:
            flash('Please select a valid payment method.')
            return redirect(url_for('booking.payment', booking_id=booking_id))

        query_db(
            "update bookings set payment_method = %s, payment_status = 'completed', status = 'confirmed' where id = %s",
            (payment_method, booking_id)
        )

        flash('Payment successful! Your booking is now confirmed.')
        return redirect(url_for('booking.booking_confirmation', booking_id=booking_id))

    return render_template('payment.html', booking=booking)


@booking_bp.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    bookings = query_db("""
        select b.*, p.package_name, p.destination_name, p.location
        from bookings b
        join packages p on b.package_id = p.id
        where b.user_id = %s
    """, (session['user_id'],), fetch=True)

    return render_template('my_bookings.html', bookings=bookings)