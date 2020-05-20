from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import gspread
app = Flask(__name__)

gc = gspread.service_account(filename="gsheet_credentials.json")

sh = gc.open_by_key('1XQyZJEqIxTm3dk7JGJd5Zprkd_XfQJXOFjwTOGtx2B4')
worksheet = sh.sheet1


class Post:
    def __init__(self, message, time, done, row_idx):
        self._message = message
        self._time = time
        self._done = done
        self._row_idx = row_idx


def get_date_time(date_time_str):
    date_time_obj = None
    error_code = None
    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        error_code = f"Error ! {e}"
    if date_time_obj is not None:
        now_time_cet = datetime.utcnow() + timedelta(hours=2)
        if not date_time_obj > now_time_cet:
            error_code = "error! can not schedule in the past"

    return date_time_obj, error_code


@app.route('/')
def post_list():
    post_records = worksheet.get_all_records()
    posts = []
    for idx, post in enumerate(post_records, start=2):
        post = Post(**post, row_idx=idx)
        posts.append(post)
    posts.reverse()
    n_open_posts = sum(1 for post in posts if not post._done)
    return render_template('base.html', posts=posts, n_open_posts=n_open_posts)


@app.route('/post', methods=['POST'])
def add_post():
    message = request.form['message']
    if not message:
        return "error! no message"
    time = request.form['time']
    if not time:
        return "error! no time"
    pw = request.form['pw']
    if not pw or pw != "12345":
        return "error! wrong password"

    date_time_obj, error_code = get_date_time(date_time_str=time)
    if error_code is not None:
        return error_code

    post = [str(date_time_obj), message, 0]
    worksheet.append_row(post)
    return redirect('/')


@app.route('/delete/<int:row_idx>')
def delete_post(row_idx):
    worksheet.delete_rows(row_idx)
    return redirect('/')
