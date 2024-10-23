from flask import Flask, render_template, request, redirect, url_for, session
import random
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# CSVファイルから問題を読み込む関数
def load_questions(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# カテゴリと対応するCSVファイルのマッピング
category_files = {
    'danger': './data/Danger.csv',
    'legal': './data/Legal.csv',
    'product': './data/Product.csv',
    'account': './data/Account.csv'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_category', methods=['POST'])
def select_category():
    category = request.form['category']
    session['category'] = category
    session['questions'] = random.sample(load_questions(category_files[category]), 10)
    session['current_question'] = 0
    session['correct_answers'] = 0
    session['answered'] = False
    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    if session.get('current_question') is None:
        return redirect(url_for('index'))

    # 現在の質問を表示
    current_question = session['questions'][session['current_question']]
    current_question_number = session['current_question'] + 1
    return render_template(
        'question.html', 
        question=current_question, 
        current_question_number=current_question_number, 
        show_next=session.get('answered', False)
    )

@app.route('/answer', methods=['POST'])
def answer():
    # 解答送信時の処理
    user_answer = int(request.form['answer'])
    correct_answer = int(session['questions'][session['current_question']]['answer'])

    session['user_answer'] = user_answer
    session['correct_answer'] = correct_answer
    session['answered'] = True  # 解答済みフラグ

    # 正解数の更新
    if user_answer == correct_answer:
        session['correct_answers'] += 1

    return redirect(url_for('question'))

@app.route('/next', methods=['POST'])
def next_question():
    session['answered'] = False
    session['current_question'] += 1

    if session['current_question'] >= len(session['questions']):
        return redirect(url_for('result'))

    return redirect(url_for('question'))

@app.route('/result')
def result():
    correct = session['correct_answers']
    total = len(session['questions'])
    return render_template('result.html', correct=correct, total=total)

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)