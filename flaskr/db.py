import sqlite3
import click # 터미널에서 실행, 빌트인, 확장, 어플리케이션에서 정의한 명령어 사용 가능하게 함.
from flask import current_app, g # g는 각 request에 대한 객체, current_app은 현재 어플리케이션이 위치한 경로의 sql 파일 읽어오기
from flask.cli import with_appcontext # command와 extensions이 어플리케이션 및 환경설정에 접근할 수 있게 함.


def get_db(): #

    if 'db' not in g:
        g.db = sqlite3.connect( 
            current_app.config['DATABASE'], # DATABASE에 연결, Row 단위로 데이터 가져옴
            detect_types=sqlite3.PARSE_DECLTYPES # 컬럼 데이터의 타입 판별
        )
        g.db.row_factory = sqlite3.Row # 튜플 형태로 데이터의 row 출력, row_factory 객체로 저장하여 사용

    return g.db


def close_db(e=None):

    db = g.pop('db', None)
    if db is not None:
        db.close()



def init_db(): # get_db()호출 -> flask, sqlite 연결하는 객체 생성, 그 객체로 sql script 실행

    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8')) # 여러 개의 sql문을 한 번에 실행


@click.command('init-db') # init_db()는 cmd에서 init-db라는 이름으로 실행됨.
@with_appcontext
def init_db_command():
    init_db()



def init_app(app):

    app.teardown_appcontext(close_db) # response를 리턴할 때마다 close_db 실행(객체 제거)
    app.cli.add_command(init_db_command) #init_db_command를 flask command로 추가

