from flask import Flask, render_template, request, redirect, Response
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    message = ""
    message_type = ""

    if request.method == 'POST':

        name = request.form['name'].strip()
        email = request.form['email'].strip()

        try:

            if len(name) == 0:
                message = "Please enter a name."
                message_type = "error"

            else:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (name, email)
                )

                conn.commit()
                conn.close()

                message = "Data Saved Successfully!"
                message_type = "success"

        except sqlite3.IntegrityError:
            message = "Duplicate Email Found!"
            message_type = "error"

        except Exception as e:
            print("ERROR:", e)
            message = f"Error: {e}"
            message_type = "error"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT email
            FROM users
            GROUP BY email
            HAVING COUNT(*) > 1
        )
    """)
    duplicate_count = cursor.fetchone()[0]

    search = request.args.get('search', '')

    if search:
        cursor.execute(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
            (f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    search_results = len(users)

    conn.close()

    return render_template(
        'index.html',
        message=message,
        message_type=message_type,
        users=users,
        total_users=total_users,
        search_results=search_results,
        duplicate_count=duplicate_count,
        search=search
    )


@app.route('/export')
def export():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()

    csv_data = "ID,Name,Email\n"

    for user in users:
        csv_data += f"{user[0]},{user[1]},{user[2]}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=users.csv"
        }
    )


@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']

        cursor.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, id)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (id,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        'edit.html',
        user=user
    )


import os

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )