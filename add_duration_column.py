import sqlite3

# Connect to your database
conn = sqlite3.connect('gym.db')  # Ensure 'gym.db' is your database name
c = conn.cursor()

# Add the 'duration' column to the 'workouts' table
try:
    c.execute("ALTER TABLE workouts ADD COLUMN duration INTEGER")
    print("Column 'duration' added successfully.")
except sqlite3.OperationalError as e:
    print(f"Error: {e}")

# Commit changes and close the connection
conn.commit()
conn.close()
