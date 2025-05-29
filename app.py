from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'survey_data.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

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
            dob = request.form.get('dob')
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
            app.logger.error(f"Error submitting survey: {e}") # Log the error
            print(f"Error: {e}") # For debugging
            # Consider a more user-friendly error page
            return "An error occurred while submitting your response. Please ensure all required fields are filled correctly.", 500

    return redirect(url_for('survey_form'))

@app.route('/thankyou')
def thank_you():
    # You might want a different thank you page design too
    return render_template('thank_you.html')

@app.route('/results') # Changed from /analysis to /results to match nav link
def view_survey_results():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Total responses
    cursor.execute("SELECT COUNT(*) as total_responses FROM responses")
    total_responses_row = cursor.fetchone()
    total_responses = total_responses_row['total_responses'] if total_responses_row else 0

    # 2. Favorite Food Counts
    # Using SUM() because we store 1 for checked, 0 for not.
    cursor.execute("""
        SELECT
            SUM(favorite_food_pizza) as pizza_count,
            SUM(favorite_food_pasta) as pasta_count,
            SUM(favorite_food_pap_wors) as pap_wors_count,
            SUM(favorite_food_other) as other_count,
            GROUP_CONCAT(CASE WHEN favorite_food_other_text IS NOT NULL AND favorite_food_other_text != '' THEN favorite_food_other_text ELSE NULL END) as other_texts
        FROM responses
    """)
    food_counts = cursor.fetchone()

    # 3. Average Likert Scale Ratings (1=Strongly Agree ... 5=Strongly Disagree)
    # Lower average means more agreement
    cursor.execute("""
        SELECT
            AVG(movies_rating) as avg_movies,
            AVG(radio_rating) as avg_radio,
            AVG(eat_out_rating) as avg_eat_out,
            AVG(tv_rating) as avg_tv
        FROM responses
    """)
    avg_ratings = cursor.fetchone()
    
    # 4. Count number of people who filled out the survey (based on non-null names or email)
    cursor.execute("SELECT COUNT(DISTINCT email) as unique_respondents FROM responses WHERE email IS NOT NULL AND email != ''")
    unique_respondents_row = cursor.fetchone()
    unique_respondents = unique_respondents_row['unique_respondents'] if unique_respondents_row else 0


    # 5. Calculate age from DOB (More complex, SQLite specific date functions)
    # For simplicity, we'll just count how many DOBs are entered
    # A more robust solution would parse DOBs and calculate actual ages
    cursor.execute("SELECT COUNT(dob) as dob_entries FROM responses WHERE dob IS NOT NULL AND dob != ''")
    dob_entries_row = cursor.fetchone()
    dob_entries = dob_entries_row['dob_entries'] if dob_entries_row else 0
    
    
    cursor.execute("SELECT COUNT(*) as adults_approx FROM responses WHERE SUBSTR(dob, 1, 4) < '2006'") # Example
    adults_approx_row = cursor.fetchone()
    adults_approx = adults_approx_row['adults_approx'] if adults_approx_row else 0


    conn.close()

    return render_template('analysis.html',
                           total_responses=total_responses,
                           unique_respondents=unique_respondents,
                           dob_entries=dob_entries,
                           adults_approx=adults_approx,
                           food_counts=food_counts,
                           avg_ratings=avg_ratings
                           )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)