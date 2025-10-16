from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Task
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")  # for flash messages
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        status = request.args.get("status")
        q = Task.query
        if status:
            q = q.filter_by(status=status)
        tasks = q.order_by(Task.created_at.desc()).all()
        return render_template("index.html", tasks=tasks, active=status or "all")

    @app.route("/create", methods=["GET", "POST"])
    def create():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            status = request.form.get("status", "todo")
            if not title:
                flash("Title is required", "danger")
                return redirect(url_for("create"))
            t = Task(title=title, description=description, status=status)
            db.session.add(t)
            db.session.commit()
            flash("Task created", "success")
            return redirect(url_for("index"))
        return render_template("form.html", action="Create", task=None)

    @app.route("/edit/<int:task_id>", methods=["GET", "POST"])
    def edit(task_id):
        task = Task.query.get_or_404(task_id)
        if request.method == "POST":
            task.title = request.form.get("title", "").strip()
            task.description = request.form.get("description", "").strip()
            task.status = request.form.get("status", "todo")
            if not task.title:
                flash("Title is required", "danger")
                return redirect(url_for("edit", task_id=task.id))
            db.session.commit()
            flash("Task updated", "success")
            return redirect(url_for("index"))
        return render_template("form.html", action="Update", task=task)

    @app.route("/delete/<int:task_id>", methods=["POST"])
    def delete(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted", "info")
        return redirect(url_for("index"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)