from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用の秘密鍵


# グローバル変数として質問データを保持
questions = []

# トップページ（カテゴリ選択用）
@app.route("/")
def index():
    return render_template("index.html")


# カテゴリ選択時の処理
@app.route("/select_category", methods=["POST"])
def select_category():
    global questions  # グローバル変数を使用
    # ユーザーが選択したカテゴリをセッションに保存
    category = request.form.get("category")
    session['category'] = category
    if category == "danger":
        session['カテゴリ'] = '危険選択'
    elif category == "legal":
        session['カテゴリ'] = '約款と法律'
    elif category == "product":
        session['カテゴリ'] = '生命保険商品と営業'
    elif category == "account":
        session['カテゴリ'] = '生命保険会計'

    # 選択に基づいて対応するCSVを読み込み
    if category == "danger":
        csv_file = "./data/Danger.csv"
    elif category == "legal":
        csv_file = "./data/Legal.csv"
    elif category == "product":
        csv_file = "./data/Product.csv"
    elif category == "account":
        csv_file = "./data/Account.csv"
    else:
        return redirect(url_for('index'))  # 無効なカテゴリの場合はトップに戻る
    
    # CSVファイルを読み込み、質問データを作成
    try:
        data = pd.read_csv(csv_file, encoding='utf-8')
    except FileNotFoundError:
        return f"CSVファイルが見つかりません: {csv_file}"

    # 質問データをグローバル変数に保存（セッションに保存しない）
    questions = [
        {
            "id": index,
            "question": row["question"],
            "answer": row["answer"],
            "explanation": row["explanation"]
        }
        for index, row in data.iterrows()
    ]
    
    session['used_questions'] = []  # 使用済みの質問IDを記録するリスト
    session['current_question'] = 0  # 現在の質問インデックスを初期化

    return redirect(url_for('question'))


# 質問の表示と回答
@app.route("/question", methods=["GET", "POST"])
def question():
    global questions  # グローバル変数を使用
    if not questions:
        return redirect(url_for('index'))  # 質問データが存在しない場合はトップに戻る

    # 使用済みの質問リストを取得
    used_questions = session.get('used_questions', [])

    # すべての問題を表示し終えた場合は終了ページへ
    if len(used_questions) >= len(questions):
        return render_template("complete.html")

    # カテゴリ選択後のGETリクエスト時には未使用の質問をランダムに選択
    if request.method == "GET":
        remaining_questions = [q for q in questions if q['id'] not in used_questions]
        question = random.choice(remaining_questions)
        session['current_question'] = question['id']  # 現在の質問IDをセッションに保存

        return render_template(
            "question.html", 
            category = session['カテゴリ'],
            question = question, 
            result = None, 
            explanation = None, 
            show_next = False
        )

    # POSTメソッドで解答が送信された場合
    if request.method == "POST":
        # 現在の質問IDから質問を特定
        current_question_id = session.get('current_question')
        question = next((q for q in questions if q['id'] == current_question_id), None)
        
        if 'answer' in request.form:  # 解答が送信されたとき
            user_answer = int(request.form["answer"])
            correct_answer = int(question["answer"])
            explanation = question["explanation"]
            result = "正解" if user_answer == correct_answer else "不正解"
            
            # 質問IDを使用済みリストに追加し、セッションを更新
            used_questions.append(current_question_id)
            session['used_questions'] = used_questions

            return render_template(
                "question.html", 
                category = session['カテゴリ'],
                user_answer = "正しい" if user_answer == 1 else "誤り",
                correct_answer = "正しい" if correct_answer == 1 else "誤り",
                question = question, 
                result = result, 
                explanation = explanation, 
                show_next=True
            )

        elif 'next' in request.form:  # 次の問題ボタンが押されたとき
            return redirect(url_for('question'))

    return redirect(url_for('index'))


@app.route("/reset")
def reset():
    # セッションをリセットし、最初の問題に戻る
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
