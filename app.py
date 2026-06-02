from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

# Create the Flask application instance
app = Flask(__name__)

# Configure the database connection
# sqlite:///todo.db means:
# - Use SQLite as the database
# - Create a file called todo.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"


# Create the SQLAlchemy database object
# This allows us to:
# - Create models (tables)
# - Query data
# - Add, update and delete records
db = SQLAlchemy(app)


# Task model
# Each Task object represents one row in the database table
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


tasks = []


@app.route("/", methods=["GET", "POST"])
def home():

    # Check if the user has submitted the form
    if request.method == "POST":

        # Get the task text from the form input
        task_text = request.form.get("task")

        # Only continue if the task is not empty
        if task_text:

            # Create a new Task object
            # This creates a new row ready to be inserted into the database
            new_task = Task(text=task_text)

            # Add the new task to the database session
            db.session.add(new_task)

            # Commit the transaction and save the task permanently
            db.session.commit()

        # Redirect back to the home page
        # Prevents duplicate submissions when the page is refreshed
        return redirect(url_for("home"))

    # Retrieve all tasks from the database
    tasks = Task.query.order_by(Task.created_at.desc()).all()

    # Count how many tasks are not completed
    remaining_tasks = Task.query.filter_by(completed=False).count()

    # Render the template and pass data into Jinja
    return render_template("index.html", tasks=tasks, remaining_tasks=remaining_tasks)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    task = Task.query.get_or_404(id)

    if request.method == "POST":

        updated_text = request.form.get("task")

        if updated_text:

            task.text = updated_text

            db.session.commit()

            return redirect(url_for("home"))

    return render_template("edit.html", task=task)


@app.route("/delete/<int:id>")
def delete_task(id):

    # Find the task by its database ID
    task = Task.query.get_or_404(id)

    # Delete the task from the database session
    db.session.delete(task)

    # Save the deletion permanently
    db.session.commit()

    return redirect(url_for("home"))


@app.route("/complete/<int:id>")
def toggle_complete(id):

    # Find the task by its database ID
    # If it does not exist, Flask shows a 404 page
    task = Task.query.get_or_404(id)

    # Flip completed status
    task.completed = not task.completed

    # Save the update to the database
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":

    # Create an application context
    with app.app_context():
        # Creates all database tables defined by models
        db.create_all()

    app.run(debug=True)
