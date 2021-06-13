# 회원가입, 로그인, 로그아웃

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/sign_up', methods=('GET', 'POST'))
def sign_up(): # 회원가입

    if request.method == 'POST': # 유저로부터 id/pw의 데이터를 전달받음
        username = request.form['username']
        password = request.form['password']
        db = get_db()  # DB 불러옴
        error = None

        if not username: # Username 비어있는 경우
            error = 'Username is empty.'
        elif not password: # Pw 비어있는 경우
            error = 'Password is empty.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None: # DB에 이미 있는 정보일 때
            error = 'User {} is already registered.'.format(username)

        if error is None: # 정상적인 회원가입
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password)) # User의 비밀번호를 hash로 변환하여 저장
            )
            db.commit()

            return redirect(url_for('auth.sign_in')) # 전달받은 name을 통해 url 생성, 해당 url의 function으로 이동
        flash(error) # 회원가입 오류 시 메시지 전달

    return render_template('auth/sign_up.html') # auth/sign_up.html 렌더링


@bp.route('/sign_in', methods=('GET', 'POST'))
def sign_in(): # 로그인

    if request.method == 'POST': # 유저로부터 id/pw의 데이터를 전달받음
        username = request.form['username']
        password = request.form['password']
        db = get_db() # DB 불러옴
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Check your ID again.'
        elif not check_password_hash(user['password'], password): # password를 hash로 변환하여 DB에 저장된 data와 같은 값인지 확인
            error = 'Check your pw again.'

        if error is None:
            session.clear()
            session['user_id'] = user['id'] # ID/PW 일치하면 세션에 유저의 아이디 등록함(다른 페이지에서도 로그인 상태 유지)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/sign_in.html')


@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id') # 세션에서 user_id 가져옴

    if user_id is None: # 유저에 대한 기록이 없다면 None
        g.user = None
    else: # 유저에 대한 기록이 있다면 g.user에 DB에 기록된 정보 저장
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/sign_out')
def sign_out(): # 유저가 /auth/logout 요청하면 세션 초기화(로그아웃)

    session.clear()
    return redirect(url_for('index'))


def sign_in_required(view):

    @functools.wraps(view) # Decorator
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.sign_in'))

        return view(**kwargs)

    return wrapped_view