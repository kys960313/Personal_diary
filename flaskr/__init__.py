import os

from flask import Flask


def create_app(test_config=None): # 플라스크 인스턴스 생성, 환경설정

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), # DB파일 저장 경로(app.instance_path 하위에 저장됨)
    )


    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
	

    try: # instance 폴더 생성
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db #db.py을 불러온다.
    db.init_app(app) # init_app 함수에 생성된 어플리케이션을 인자로 전달

    from . import auth
    app.register_blueprint(auth.bp) # auth 모듈의 bp 객체를 앱에 블루프린트로 등록
    # 뷰와 코드는 블루프린트에 등록, 블루프린트는 앱에 등록됨.
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    


    return app