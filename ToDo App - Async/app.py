from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=True, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description} {self.completed}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref = "list", lazy=True)
    completed = db.Column(db.Boolean, nullable=True, default=False)

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
    todos =Todo.query.filter_by(list_id=list_id).order_by('id').all(), 
    lists = TodoList.query.all(),
    active_list=TodoList.query.get(list_id))

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    # Important error catching routine
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']

        new_todo = Todo(description=description)
        new_todo.list_id = list_id
        db.session.add(new_todo)
        db.session.commit()
        body['description'] = new_todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if not error:
        return jsonify(body)

@app.route('/todos/create_list', methods=['POST'])
def create_list():
    error = False
    body = {}
    # Important error catching routine
    try:
        list_name = request.get_json()['list_name']

        new_list = TodoList(name=list_name)
        db.session.add(new_list)
        db.session.commit()
        body['list_name'] = new_list.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if not error:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<list_id>/set-list-completed', methods=['POST'])
def set_completed_list_todo(list_id):
    try:
        completed = request.get_json()['completed']
        todos = Todo.query.filter_by(list_id=list_id).all()
        for todo in todos:
            todo.completed = completed;
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/todos/<list_id>/delete-list', methods=['DELETE'])
def delete_list(list_id):
    try:
        todos = Todo.query.filter_by(list_id=list_id).all()
        for todo in todos:
            todo.list_id = 1;
        list1 = TodoList.query.get(list_id)
        db.session.delete(list1)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return jsonify({ 'success': True })

if __name__ == '__main__':
    app.run(debug=True)