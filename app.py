from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# CSVからデータを読み込み
data = pd.read_csv("危険.csv")

# 一問一答形式の問題データを生成
questions = [
    {
        "id": index,
        "question": row["問題"],
        "answer": "正しい" if row["正誤"] == 1 else "誤り",
        "explanation": row["解答"]
    }
    for index, row in data.iterrows()
]

# ホームページ (問題の表示)
@app.route("/")
def index():
    return render_template("index.html", questions=questions)

# 答えの送信と結果表示
@app.route("/submit", methods=["POST"])
def submit():
    question_id = int(request.form["question_id"])
    user_answer = request.form["answer"]
    correct_answer = questions[question_id]["answer"]
    explanation = questions[question_id]["explanation"]

    result = "正解" if user_answer == correct_answer else "不正解"
    return render_template("result.html", question=questions[question_id], result=result, explanation=explanation)

if __name__ == "__main__":
    app.run(debug=True)
