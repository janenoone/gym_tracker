from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    c = conn.cursor()
    try:
        # Create the workouts table if it doesn't exist
        c.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movement TEXT NOT NULL,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                duration INTEGER,
                distance REAL,
                notes TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/log')
def log_workout():
    return render_template('log.html')

@app.route('/log/upper-body', methods=['GET', 'POST'])
def log_upper_body():
    if request.method == 'POST':
        conn = sqlite3.connect('gym.db', check_same_thread=False)
        c = conn.cursor()

        try:
            # Generate a unique workout_id for this workout
            c.execute("SELECT MAX(workout_id) FROM workouts")
            last_workout_id = c.fetchone()[0]
            workout_id = (last_workout_id or 0) + 1

            # Loop through 5 movements, each with up to 5 sets
            for movement_index in range(5):
                movement = request.form.get(f'movement{movement_index}')
                notes = request.form.get(f'notes{movement_index}')

                # Only process if a movement is provided
                if movement:
                    for set_index in range(5):
                        reps = request.form.get(f'reps{movement_index}_{set_index}')
                        weight = request.form.get(f'weight{movement_index}_{set_index}')

                        # Insert each set into the database if reps and weight are provided
                        if reps and weight:
                            c.execute(
                                "INSERT INTO workouts (workout_id, movement, sets, reps, weight, notes, date) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
                                (workout_id, movement, set_index + 1, reps, weight, notes)
                            )

            conn.commit()
        except sqlite3.Error as e:
            return f"Database error: {e}", 500
        finally:
            conn.close()

        return redirect('/history')

    return render_template('log_upper_body.html')


@app.route('/log/lower-body', methods=['GET', 'POST'])
def log_lower_body():
    if request.method == 'POST':
        conn = sqlite3.connect('gym.db', check_same_thread=False)
        c = conn.cursor()

        try:
            # Process 5 movements, each with 5 sets
            for movement_index in range(5):
                movement = request.form.get(f'movement{movement_index}')
                notes = request.form.get(f'notes{movement_index}')

                # Only process if a movement is provided
                if movement:
                    # Loop through 5 sets for each movement
                    for set_index in range(5):
                        reps = request.form.get(f'reps{movement_index}_{set_index}')
                        weight = request.form.get(f'weight{movement_index}_{set_index}')

                        # Insert each set into the database if reps and weight are provided
                        if reps and weight:
                            c.execute(
                                "INSERT INTO workouts (movement, sets, reps, weight, notes, date) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                                (movement, set_index + 1, reps, weight, notes)
                            )

            conn.commit()  # Commit all inserts
        except sqlite3.Error as e:
            return f"Database error: {e}", 500  # Return error if something goes wrong
        finally:
            conn.close()  # Ensure the connection is always closed

        return redirect('/history')  # Redirect to the history page

    # Render the template for GET requests
    return render_template('log_lower_body.html')



@app.route('/log/cardio', methods=['GET', 'POST'])
def log_cardio():
    if request.method == 'POST':
        # Retrieve form data
        movement = request.form.get('movement')
        duration = request.form.get('duration')
        distance = request.form.get('distance')
        notes = request.form.get('notes')

        # Validate required fields
        if not movement or not duration:
            return "Error: Movement and duration are required fields!", 400

        try:
            conn = sqlite3.connect('gym.db', check_same_thread=False)
            c = conn.cursor()
            c.execute(
                "INSERT INTO workouts (movement, duration, distance, notes, date) VALUES (?, ?, ?, ?, datetime('now'))",
                (movement, duration, distance, notes)
            )
            conn.commit()
        finally:
            conn.close()

        return redirect('/history')

    return render_template('log_cardio.html')

@app.route('/history')
def history():
    conn = sqlite3.connect('gym.db', check_same_thread=False)
    c = conn.cursor()

    # Fetch grouped workouts
    c.execute("""
        SELECT workout_id, date, GROUP_CONCAT(movement || ' (Set ' || sets || ': ' || reps || ' reps, ' || weight || 'kg)', '\n') AS movements
        FROM workouts
        GROUP BY workout_id, date
        ORDER BY date DESC
    """)
    rows = c.fetchall()

    conn.close()

    # Transform rows into a usable format
    history = [
        {
            'workout_id': row[0],
            'date': row[1],
            'movements': row[2].split('\n')  # Split concatenated movements into a list
        }
        for row in rows
    ]

    return render_template('history.html', history=history)

@app.route('/performance')
def performance():
    try:
        conn = sqlite3.connect('gym.db', check_same_thread=False)
        c = conn.cursor()
        # Example query to calculate performance metrics (adjust as needed)
        c.execute("""
            SELECT movement, MAX(weight), date 
            FROM workouts 
            WHERE weight IS NOT NULL 
            GROUP BY movement
        """)
        performance_data = c.fetchall()
    finally:
        conn.close()

    return render_template('performance.html', performance=performance_data)

@app.route('/personal-records')
def personal_records():
    try:
        conn = sqlite3.connect('gym.db', check_same_thread=False)
        c = conn.cursor()
        # Example query to fetch personal records (adjust as needed)
        c.execute("""
            SELECT movement, MAX(weight) AS max_weight, date 
            FROM workouts 
            WHERE weight IS NOT NULL 
            GROUP BY movement
        """)
        personal_records = c.fetchall()
    finally:
        conn.close()

    return render_template('personal_records.html', records=personal_records)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
