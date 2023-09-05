#login_api.py
from flask_restful import Resource
from flask import request, session
from models import db
from facades import AnonymousFacade, LoginToken, FacadeBase
from logger_config import logger



anonymous_facade = FacadeBase(db_session=db.session)  


class LoginResource(Resource):
    def __init__(self, facade, anonymous_facade):
        self.facade =  facade
        self.anonymous_facade = anonymous_facade


    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            self.anonymous_facade.login(username, password)
            return {'message': 'Logged in successfully'}, 200
        except ValueError:
            return {'error': 'Invalid username or password'}, 401
        

    def get(self):
        print(f'sessiom === {session}') 

        if 'login_token' in session:
            login_token_data = session['login_token']
            print(login_token_data)
            return login_token_data, 200
            
        else:
            return {'message': 'No user is currently logged in'}, 200




class LogoutResource(Resource):
    def post(self):
        try:
            if 'login_token' in session:
                return AnonymousFacade.logout()
            
            print('cant logout, no user singed-in')
        except Exception as e:
            logger.info (e)
