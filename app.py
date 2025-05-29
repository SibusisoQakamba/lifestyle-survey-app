from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
DATABASE = 'survey_data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def calculate_age(born_date_str):
    if not born_date_str:
        return None
    try:
        # Ensure the date string is in YYYY-MM-DD format for fromisoformat
        # HTML input type="date" should provide this format
        born = date.fromisoformat(born_date_str)
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except ValueError:
        # Handle cases where date string might not be valid
        app.logger.warning(f"Invalid date format for DOB: {born_date_str}")
        return None

@app.route('/')
def survey_form():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit_survey():
    if request.method == 'POST':
        try:
            # Personal Details
            full_names = request.form.get('full_names')
            email = request.form.get('email')
            dob = request.form.get('dob') # Expected YYYY-MM-DD
            contact_number = request.form.get('contact_number')

            # Favorite Food
            food_pizza = 1 if request.form.get('food_pizza') else 0
            food_pasta = 1 if request.form.get('food_pasta') else 0
            food_pap_wors = 1 if request.form.get('food_pap_wors') else 0
            food_other_checkbox = 1 if request.form.get('food_other_checkbox') else 0
            food_other_text = request.form.get('food_other_text') if food_other_checkbox else None

            # Likert Scale
            movies_rating = request.form.get('movies_rating', type=int)
            radio_rating = request.form.get('radio_rating', type=int)
            eat_out_rating = request.form.get('eat_out_rating', type=int)
            tv_rating = request.form.get('tv_rating', type=int)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO responses (
                    full_names, email, dob, contact_number,
                    favorite_food_pizza, favorite_food_pasta, favorite_food_pap_wors,
                    favorite_food_other, favorite_food_other_text,
                    movies_rating, radio_rating, eat_out_rating, tv_rating
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                full_names, email, dob, contact_number,
                food_pizza, food_pasta, food_pap_wors,
                food_other_checkbox, food_other_text,
                movies_rating, radio_rating, eat_out_rating, tv_rating
            ))
            conn.commit()
            conn.close()
            return redirect(url_for('thank_you'))
        except Exception as e:
            app.logger.error(f"Error submitting survey: {e}")
            print(f"Error: {e}") # For debugging
            return "An error occurred while submitting your response. Please ensure all required fields are filled correctly.", 500

    return redirect(url_for('survey_form'))

@app.route('/thankyou')
def thank_you():
    return render_template('thank_you.html')

@app.route('/results')
def view_survey_results():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_responses FROM responses")
    total_responses_row = cursor.fetchone()
    total_responses = total_responses_row['total_responses'] if total_responses_row else 0

    avg_age_val = "N/A"
    max_age_val = "N/A"
    min_age_val = "N/A"
    food_counts_val = None
    avg_ratings_val = None

    if total_responses > 0:
        cursor.execute("SELECT dob FROM responses WHERE dob IS NOT NULL AND dob != ''")
        dobs = cursor.fetchall()
        ages = []
        for row in dobs:
            age = calculate_age(row['dob'])
            if age is not None:
                ages.append(age)

        if ages:
            avg_age_val = round(sum(ages) / len(ages), 1)
            max_age_val = max(ages)
            min_age_val = min(ages)
        else: # No valid DOBs to calculate age from
            avg_age_val = "N/A (No valid DOBs)"
            max_age_val = "N/A (No valid DOBs)"
            min_age_val = "N/A (No valid DOBs)"

        cursor.execute("""
            SELECT
                SUM(favorite_food_pizza) as pizza_count,
                SUM(favorite_food_pasta) as pasta_count,
                SUM(favorite_food_pap_wors) as pap_wors_count
            FROM responses
        """)
        food_counts_val = cursor.fetchone()

        cursor.execute("""
            SELECT
                AVG(movies_rating) as avg_movies,
                AVG(radio_rating) as avg_radio,
                AVG(eat_out_rating) as avg_eat_out,
                AVG(tv_rating) as avg_tv
            FROM responses
        """)
        avg_ratings_val = cursor.fetchone()

    conn.close()

    return render_template('analysis.html',
                           total_responses=total_responses,
                           avg_age=avg_age_val,
                           max_age=max_age_val,
                           min_age=min_age_val,
                           food_counts=food_counts_val,
                           avg_ratings=avg_ratings_val
                           )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)