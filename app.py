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
            age = request.form.get('age', type=int) # Use .get for safety, add type
            gender = request.form['gender']
            preferred_activity = request.form['preferred_activity']
            preferred_environment = request.form['preferred_environment']
            social_preference = request.form['social_preference']
            tech_usage = request.form['tech_usage']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO responses (age, gender, preferred_activity, preferred_environment, social_preference, tech_usage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (age, gender, preferred_activity, preferred_environment, social_preference, tech_usage))
            conn.commit()
            conn.close()
            return redirect(url_for('thank_you'))
        except Exception as e:
            # Log the error e.g., app.logger.error(f"Error submitting survey: {e}")
            print(f"Error: {e}") # For debugging
            # Optionally, redirect to an error page or show a message
            return "An error occurred while submitting your response. Please try again.", 500

    return redirect(url_for('survey_form')) # If not POST, redirect back

@app.route('/thankyou')
def thank_you():
    return render_template('thank_you.html')

@app.route('/analysis')
def analysis():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Total responses
    cursor.execute("SELECT COUNT(*) as total_responses FROM responses")
    total_responses = cursor.fetchone()['total_responses']

    # 2. Average age
    cursor.execute("SELECT AVG(age) as avg_age FROM responses WHERE age IS NOT NULL")
    avg_age_row = cursor.fetchone()
    avg_age = round(avg_age_row['avg_age'], 1) if avg_age_row and avg_age_row['avg_age'] is not None else "N/A"


    # 3. Gender distribution
    cursor.execute("SELECT gender, COUNT(*) as count FROM responses GROUP BY gender ORDER BY count DESC")
    gender_distribution = cursor.fetchall()

    # 4. Most popular activity
    cursor.execute("""
        SELECT preferred_activity, COUNT(*) as count
        FROM responses
        GROUP BY preferred_activity
        ORDER BY count DESC
        LIMIT 5
    """)
    popular_activities = cursor.fetchall()

    # 5. Preferred environment distribution
    cursor.execute("""
        SELECT preferred_environment, COUNT(*) as count
        FROM responses
        GROUP BY preferred_environment
        ORDER BY count DESC
    """)
    environment_distribution = cursor.fetchall()

    # 6. Social preference distribution
    cursor.execute("""
        SELECT social_preference, COUNT(*) as count
        FROM responses
        GROUP BY social_preference
        ORDER BY count DESC
    """)
    social_preference_distribution = cursor.fetchall()
    
    # 7. Tech usage distribution
    cursor.execute("""
        SELECT tech_usage, COUNT(*) as count
        FROM responses
        GROUP BY tech_usage
        ORDER BY count DESC
    """)
    tech_usage_distribution = cursor.fetchall()


    conn.close()

    return render_template('analysis.html',
                           total_responses=total_responses,
                           avg_age=avg_age,
                           gender_distribution=gender_distribution,
                           popular_activities=popular_activities,
                           environment_distribution=environment_distribution,
                           social_preference_distribution=social_preference_distribution,
                           tech_usage_distribution=tech_usage_distribution
                           )

if __name__ == '__main__':
    # For development, debug=True is fine. For a public kiosk, use a production WSGI server.
    app.run(debug=True, host='0.0.0.0', port=5000)