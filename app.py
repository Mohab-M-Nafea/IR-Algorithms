import os
from flask import *
from random import *
from math import *
import sqlite3

ch = ["A", "B", "C", "D", "E", "F"]
app = Flask(__name__)


@app.route('/')
def documents():
    return '''
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Home</title>
            <link rel="stylesheet" media="screen" href="../static/bootstrap.min.css">
            <link rel="stylesheet" media="screen" href="../static/style.css">
        </head>
        <body>
            <form action = "http://127.0.0.1:5000/Created" method = "POST">
                <label for="range" style="padding-bottom: 8px">Enter number of files and click Generate</label>
                <input type="number" name = "range">
                <br>
                <input type="submit" value="Generate">
            </form>
            <br>
            <p><a href="http://127.0.0.1:5000/Statistical_Model">Statistical Model</a></p>
            <p><a href="http://127.0.0.1:5000/Vector_Space_Model">Vector Space Model</a></p>
        </body>
    </html>
    '''


@app.route('/Created', methods=["POST"])
def creat():
    num = request.form['range']

    if num == "":
        num = 10

    creat_files(int(num))
    return '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>generated</title>
                <link rel="stylesheet" media="screen" href="../static/bootstrap.min.css">
                <link rel="stylesheet" media="screen" href="../static/style.css">
            </head>
            <body>
                <h1>The generation was successful</h1>
                <br>
                <p><a href="http://127.0.0.1:5000/Statistical_Model">Statistical Model</a></p>
                <p><a href="http://127.0.0.1:5000/Vector_Space_Model">Vector Space Model</a></p>
                <p><a href="http://127.0.0.1:5000">Home</a></p>
            </body>
        </html>
        '''


@app.route('/Statistical_Model')
def statistical():
    return render_template('Statistical Model.html')


@app.route('/Statistical_Model_Result', methods=["POST"])
def statistical_result():
    string = request.form['query']
    matrix = count()
    query = query_list(string, 1)
    sim(matrix, query, 1)
    sim_score = score(matrix)
    matrix = sorted(matrix, reverse=True, key=lambda doc: matrix[doc]["score"])
    return render_template('Result.html', matrix=matrix, num=number(), sim=sim_score)


@app.route('/Vector_Space_Model')
def vector_space():
    return render_template('Vector Space Model.html')


@app.route('/Vector_Space_Model_Result', methods=["POST"])
def vector_result():
    string = request.form['query']
    matrix = count()
    query = query_list(string, 2)
    idf_array = idf()
    maximum = max(query.values())
    for char in ch:
        query[char] = (query[char]/maximum)*idf_array[char]
    weight(matrix, idf_array)
    sim(matrix, query, 2)
    sim_score = score(matrix)
    matrix = sorted(matrix, reverse=True, key=lambda doc: matrix[doc]["score"])
    return render_template('Result.html', matrix=matrix, num=number(), sim=sim_score)


@app.route('/Result_<file_name>')
def files(file_name):
    file = open(f"{file_name}.txt", "r")
    text = file.read()
    file.close()
    return f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>{file_name}</title>
                    <link rel="stylesheet" media="screen" href="../static/bootstrap.min.css">
                    <link rel="stylesheet" media="screen" href="../static/style.css">
                </head>
                <body>
                    <p>{text}</p>
                </body>
            </html>
            '''


def query_list(string, model):
    query = {}
    if model == 1:
        start = 1
        for char in ch:
            if char in string:
                end = string.index(';', start) if start < string.rindex(';') else string.index('>')
                query[char] = float(string[start + 2:end])
                start = string.index(';', start) + 1 if start < string.rindex(';') else start
            else:
                query[char] = 0
    else:
        for char in ch:
            if char in string:
                query[char] = string.count(char)
            else:
                query[char] = 0
    return query


def creat_files(num):
    directory = os.path.dirname(os.path.abspath("app.py"))
    files_in_directory = os.listdir(directory)
    text_files = [file for file in files_in_directory if file.endswith(".txt")]
    for file in text_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)

    database(num)
    for i in range(num):
        random(i)


def random(i):
    f = open(f"D{i + 1}.txt", "w")
    txt = ""
    for j in range(randint(5, 15)):
        txt += choice(ch) + " "
    f.write(txt[:len(txt) - 1])
    f.close()
    return txt


def database(num):
    db = sqlite3.connect("app.db")

    cursor = db.cursor()

    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='documents'")

    if cursor.fetchone()[0] == 0:
        cursor.execute("CREATE TABLE if not exists documents(id integer ,range integer)")
        cursor.execute(f"insert into documents(id, range) values(1, {num})")
    else:
        cursor.execute(f"update documents set range = {num} where id = 1")

    db.commit()

    db.close()


def number():
    db = sqlite3.connect("app.db")

    cursor = db.cursor()

    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='documents'")

    if cursor.fetchone()[0] == 0:
        cursor.execute("CREATE TABLE if not exists documents(id integer ,range integer)")
        cursor.execute("insert into documents(id, range) values(1, 10)")

    cursor.execute("select * from documents")
    num = cursor.fetchone()[1]

    db.commit()

    db.close()

    return num


def count():
    matrix = {}
    for i in range(number()):
        file_name = f"D{i + 1}"
        counter = {}
        try:
            file = open(f"{file_name}.txt", "r")
            text = file.read()
            file.close()
        except IOError:
            text = random(i)
        for char in ch:
            counter[char] = text.count(char)
        matrix[file_name] = counter
    return matrix


def sim(matrix, query, model):
    for i in range(number()):
        inner = 0
        if model == 1:
            for char in ch:
                inner += (matrix[f"D{i + 1}"][char]/sum(matrix[f"D{i + 1}"].values()))*query[char]
            matrix[f"D{i + 1}"]["score"] = inner
        else:
            matrix_sum = 0
            query_sum = 0
            for char in ch:
                inner += matrix[f"D{i + 1}"][char] * query[char]
                matrix_sum += pow(matrix[f"D{i + 1}"][char], 2)
                query_sum += pow(query[char], 2)

            matrix[f"D{i + 1}"]["score"] = inner/sqrt(matrix_sum*query_sum)


def idf():
    idf_array = {}
    for char in ch:
        counter = 0
        for i in range(number()):
            try:
                file = open(f"D{i+1}.txt", "r")
                text = file.read()
                file.close()
            except IOError:
                text = random(i)
            if char in text:
                counter += 1
        idf_array[char] = log(number()/counter, 2)
    return idf_array


def weight(matrix, idf_array):
    for i in range(number()):
        maximum = max(matrix[f"D{i+1}"].values())
        for char in ch:
            matrix[f"D{i+1}"][char] = (matrix[f"D{i+1}"][char]/maximum)*idf_array[char]


def score(matrix):
    sim_score = []
    for i in range(number()):
        sim_score.append(matrix[f"D{i + 1}"]["score"])
    sim_score = sorted(sim_score, reverse=True)
    return sim_score


if __name__ == '__main__':
    app.run(debug=True)
