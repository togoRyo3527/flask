from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用の秘密鍵

# トップページ（カテゴリ選択用）
@app.route("/")
def home():
    return render_template("home.html")

# カテゴリ選択時の処理
@app.route("/select_category", methods=["POST"])
def select_category():
    # ユーザーが選択したカテゴリをセッションに保存
    category = request.form.get("category")
    session['category'] = category

    # 選択に基づいて対応するCSVを読み込む
    if category == "危険選択":
        session['csv_file'] = "危険.csv"
    elif category == "約款と法律":
        session['csv_file'] = "法律.csv"
    
    # セッションを初期化して最初の状態に戻す
    session['used_questions'] = []  # 使用済みの質問IDを記録するリスト
    session['current_question'] = 0  # 現在の質問インデックスを初期化

    return redirect(url_for('question'))

# 質問の表示と回答
@app.route("/question", methods=["GET", "POST"])
def question():
    # 現在選択されているカテゴリに対応するCSVファイルを読み込む
    csv_file = session.get('csv_file')
    if not csv_file:
        return redirect(url_for('home'))  # カテゴリが選択されていない場合はトップに戻る

    # CSVファイルを読み込み、質問データを作成
    try:
        data = pd.read_csv(csv_file, encoding='utf-8')
    except FileNotFoundError:
        return f"CSVファイルが見つかりません: {csv_file}"

    # 質問データを生成
    questions = [
        {
            "id": index,
            "question": row["問題"],
            "answer": "正しい" if row["正誤"] == 1 else "誤り",
            "explanation": row["解答"]
        }
        for index, row in data.iterrows()
    ]

    # 使用済みの質問リストを取得
    used_questions = session.get('used_questions', [])
    
    # すべての問題を表示し終えた場合は終了ページへ
    if len(used_questions) >= len(questions):
        return render_template("complete.html")

    # 未使用の質問をランダムに選択
    remaining_questions = [q for q in questions if q['id'] not in used_questions]
    question = random.choice(remaining_questions)

    explanation = None
    result = None

    # POSTメソッドで解答が送信された場合
    if request.method == "POST":
        user_answer = request.form["answer"]
        correct_answer = question["answer"]
        explanation = question["explanation"]
        result = "正解" if user_answer == correct_answer else "不正解"
        
        # 質問IDを使用済みリストに追加し、セッションを更新
        used_questions.append(question['id'])
        session['used_questions'] = used_questions

    return render_template("question.html", question=question, result=result, explanation=explanation)

@app.route("/reset")
def reset():
    # セッションをリセットし、最初の問題に戻る
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
