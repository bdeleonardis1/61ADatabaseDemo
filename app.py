from flask import Flask, render_template, g, request
import random
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/categories')
def categories():
    categories = requests.get('http://jservice.io/api/categories/', data={'count': 6})
    categories_json = categories.json()
    return render_template('categories.html', categories_json=categories_json)

@app.route('/category/<category_id>')
def get_question_from_category(category_id=None):
    question_list = requests.get('http://jservice.io/api/category', data={'id': category_id}).json()['clues']
    question_obj = random.choice(question_list)
    question, answer = question_obj['question'], question_obj['answer']
    return render_template('question.html', question=question, answer=answer)

@app.route('/question')
def get_random_question():
    question_obj = requests.get('http://jservice.io/api/random').json()[0]
    question, answer = question_obj['question'], question_obj['answer']
    return render_template('question.html', question=question, answer=answer)

@app.route('/answer')
def check_answer():
    input_answer = request.args['input_answer']
    real_answer = request.args['real_answer']
    correct_answer_string = 'Correct' if input_answer.lower() == real_answer.lower() else 'Incorrect'

    con = get_db()
    cur = con.cursor()
    if correct_answer_string == 'Correct':
        cur.execute("INSERT INTO answers VALUES (1);")
    else:
        cur.execute("INSERT INTO answers VALUES (0);")
    con.commit() 

    return render_template('answer.html', input_answer=input_answer, real_answer=real_answer, correct_answer_string=correct_answer_string)

import sqlite3
DATABASE = 'jeopardydb.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/stats', methods=['GET'])
def get_stats():
    cur = get_db().cursor()
    cur.execute("SELECT COUNT(*) FROM Answers WHERE Correct=1;")
    correct = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Answers WHERE Correct=0;")
    incorrect = cur.fetchone()[0]

    return "Users have answered {} correctly and {} incorrectly for {:.2f}%".format(correct, incorrect, correct / (correct + incorrect))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
