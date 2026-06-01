# =========================================================
# LOGICVERSE - SMART TRUTH TABLE GENERATOR
# =========================================================
# FEATURES
# ✔ Modern UI
# ✔ Truth Table Generation
# ✔ Syntax Validation
# ✔ AND OR NOT XOR IMPLICATION BICONDITIONAL
# ✔ Dark / Light Mode
# ✔ Expression History
# ✔ Download CSV
# ✔ Invalid Expression Detection
#
# INSTALL:
# pip install flask pandas
#
# RUN:
# python app.py
#
# OPEN:
# http://127.0.0.1:5000
# =========================================================

from flask import Flask, render_template_string, request, send_file
import itertools
import pandas as pd
import re
from io import BytesIO

app = Flask(__name__)

history = []
latest_df = None

# =========================================================
# HTML
# =========================================================

HTML = """

<!DOCTYPE html>
<html>

<head>

    <title>LogicVerse</title>

    <style>

        *{
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:Segoe UI;
        }

        body{
            background:
            linear-gradient(135deg,#020617,#0f172a,#1e293b);

            min-height:100vh;
            color:white;
            padding:40px;
            transition:0.4s;
        }

        body.light{
            background:
            linear-gradient(135deg,#f8fafc,#dbeafe,#e0e7ff);

            color:black;
        }

        .container{
            max-width:1200px;
            margin:auto;
        }

        .title{
            text-align:center;
            font-size:55px;
            font-weight:bold;
            margin-bottom:10px;
        }

        .subtitle{
            text-align:center;
            opacity:0.8;
            margin-bottom:40px;
            font-size:18px;
        }

        .card{

            background:rgba(255,255,255,0.08);

            border-radius:25px;

            padding:35px;

            margin-bottom:30px;

            backdrop-filter:blur(10px);

            box-shadow:0 10px 30px rgba(0,0,0,0.4);
        }

        body.light .card{
            background:rgba(255,255,255,0.7);
        }

        h2{
            margin-bottom:20px;
            font-size:32px;
        }

        input{

            width:100%;
            padding:18px;

            border:none;
            border-radius:15px;

            font-size:18px;

            margin-top:10px;
            margin-bottom:20px;

            outline:none;
        }

        button{

            padding:15px 25px;

            border:none;

            border-radius:14px;

            font-size:16px;

            cursor:pointer;

            transition:0.3s;

            margin-right:10px;
        }

        button:hover{
            transform:scale(1.05);
        }

        .generate{
            background:#8b5cf6;
            color:white;
        }

        .theme{
            background:#06b6d4;
            color:white;
        }

        .download{
            background:#10b981;
            color:white;
            margin-top:20px;
        }

        .error{

            color:#ef4444;
            font-size:30px;
            font-weight:bold;
            margin-bottom:10px;
        }

        .success{
            color:#22c55e;
            font-size:28px;
            margin-bottom:15px;
        }

        table{

            width:100%;

            border-collapse:collapse;

            overflow:hidden;

            border-radius:20px;

            margin-top:20px;
        }

        th{

            background:#8b5cf6;

            padding:16px;

            color:white;
        }

        td{

            text-align:center;

            padding:14px;

            background:rgba(255,255,255,0.05);

            font-size:17px;
        }

        tr:hover{
            background:rgba(255,255,255,0.08);
        }

        .true{
            color:#22c55e;
            font-weight:bold;
        }

        .false{
            color:#ef4444;
            font-weight:bold;
        }

        .history{

            background:rgba(255,255,255,0.06);

            padding:15px;

            border-radius:12px;

            margin-top:10px;

            font-size:18px;
        }

        .guide{
            line-height:2;
            font-size:18px;
            margin-top:10px;
        }

    </style>

</head>

<body id="body">

<div class="container">

    <div class="title">
        🧠 LogicVerse
    </div>

    <div class="subtitle">
        Smart Propositional Logic Truth Table Generator
    </div>

    <div class="card">

        <h2>Enter Expression</h2>

        <form method="POST">

            <input
                type="text"
                name="expression"
                placeholder="Example: (p and q) -> r"
                required
            >

            <button class="generate">
                Generate Truth Table
            </button>

            <button
                type="button"
                class="theme"
                onclick="toggleTheme()"
            >
                Toggle Theme
            </button>

        </form>

        <div class="guide">

            <h3>Supported Operators</h3>

            <p>AND → and</p>
            <p>OR → or</p>
            <p>NOT → not</p>
            <p>XOR → ^</p>
            <p>IMPLIES → -></p>
            <p>BICONDITIONAL → <-></p>

        </div>

    </div>

    {% if error %}

    <div class="card">

        <div class="error">
            ⚠ Invalid Expression
        </div>

        <p>{{error}}</p>

    </div>

    {% endif %}

    {% if table %}

    <div class="card">

        <div class="success">
            ✅ Truth Table Generated Successfully
        </div>

        <a href="/download">
            <button class="download">
                Download CSV
            </button>
        </a>

        {{table|safe}}

    </div>

    {% endif %}

    {% if history %}

    <div class="card">

        <h2>🕒 Recent Expressions</h2>

        {% for item in history %}

            <div class="history">
                {{item}}
            </div>

        {% endfor %}

    </div>

    {% endif %}

</div>

<script>

function toggleTheme(){
    document.body.classList.toggle("light")
}

</script>

</body>

</html>

"""

# =========================================================
# CONVERT EXPRESSION
# =========================================================

def convert_expression(expr):

    expr = expr.lower()

    expr = expr.replace("<->", "==")

    expr = expr.replace("->", "<=")

    expr = expr.replace("^", "!=")

    return expr

# =========================================================
# GENERATE TRUTH TABLE
# =========================================================

def generate_truth_table(expression):

    global latest_df

    expr = convert_expression(expression)

    # variable detection
    variables = sorted(set(
        re.findall(r'\b[a-z]\b', expr)
    ))

    # remove keywords
    keywords = ['a','n','d','o','r','t']

    variables = [
        v for v in variables
        if v not in keywords
    ]

    if len(variables) == 0:
        raise Exception("Please enter a valid logical expression")

    rows = list(
        itertools.product(
            [True, False],
            repeat=len(variables)
        )
    )

    data = []

    for row in rows:

        env = dict(zip(variables, row))

        try:

            result = eval(expr, {}, env)

        except:

            raise Exception(
                "Expression contains invalid syntax"
            )

        temp = list(row)

        temp.append(result)

        data.append(temp)

    columns = [v.upper() for v in variables]

    columns.append(expression)

    df = pd.DataFrame(data, columns=columns)

    latest_df = df

    table_html = df.to_html(index=False)

    table_html = table_html.replace(
        "True",
        "<span class='true'>TRUE</span>"
    )

    table_html = table_html.replace(
        "False",
        "<span class='false'>FALSE</span>"
    )

    return table_html

# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET", "POST"])

def home():

    table = None
    error = None

    if request.method == "POST":

        expression = request.form["expression"]

        history.insert(0, expression)

        if len(history) > 5:
            history.pop()

        try:

            table = generate_truth_table(expression)

        except Exception as e:

            error = str(e)

    return render_template_string(

        HTML,

        table=table,

        error=error,

        history=history
    )

# =========================================================
# DOWNLOAD CSV
# =========================================================

@app.route("/download")

def download():

    global latest_df

    output = BytesIO()

    latest_df.to_csv(output, index=False)

    output.seek(0)

    return send_file(

        output,

        mimetype="text/csv",

        as_attachment=True,

        download_name="truth_table.csv"
    )

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)