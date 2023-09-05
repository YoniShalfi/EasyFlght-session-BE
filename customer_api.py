#cusrtomer_api.py
from flask import session, request, jsonify
from flask_restful import Resource, marshal_with, fields
from facades import AdministratorFacade, LoginToken, CustomerFacade, AnonymousFacade
from models import db



facade = AdministratorFacade(dal="dal", login_token='login_token')  

class CustomerResource(Resource):
    def get(self, customer_id=None):
        login_token = LoginToken(id=session.get('id'), name=session.get('name'), role=session.get('role'), user=session.get('user'))
        admin_facade = AdministratorFacade(db.session, login_token)

        if customer_id is not None:
            customer, status = admin_facade.get_customer_by_id(customer_id)
            if status == 200:
                print(f'queried from api: {customer}')
                return customer
            return {'error': 'customer not found'}, 404
        else:
            customers, _ = admin_facade.get_all_customers()
            print(f'queried from api: {customers}')
            return customers
        
        
    def delete(self, customer_id):
        try:
            login_token = LoginToken(id=session.get('id'), name=session.get('name'), role=session.get('role'), user=session.get('user'))
            admin_facade = AdministratorFacade(db.session, login_token)

            login_token = session['login_token']
            if login_token.get('role') != 'Administrator':
                return {'error': 'Unauthorized access'}, 403


            response, status_code = admin_facade.remove_customer(customer_id)
            return response, status_code

        except Exception as e:
            print(f' error from api: {e}')
            return {'error': 'Invalid request'}, 400

        

    def put(self):
        try:
            data = request.get_json()
            login_token = session.get('login_token')
            logged_in_user_name = login_token.get('name')
            
            customer_facade = CustomerFacade(db.session)
            
            response, status_code = customer_facade.update_customer(logged_in_user_name, data)
            print(f'resp from api = {response}')
            return {'put method':'worked, your data updated'}
        
        except Exception as e:
            print(f' error from api: {e}')
            return {'error': 'Invalid request'}, 400
        

    def post(self):
        """
        Adds a new customer.
        """
        try:
            data = request.get_json()

            required_fields = ['first_name', 'last_name', 'address', 'phone_no', 'credit_card_num', 'username', 'password', 'email']
            if not all(field in data for field in required_fields):
                return {'error': 'Missing required fields'}, 400
            
            facade = AnonymousFacade(db_session=db.session)
            
            customer = facade.add_customer(data['first_name'], data['last_name'], data['address'], data['phone_no'], 
                                           data['credit_card_num'], data['username'], data['password'], data['email'])
            
            return customer , 201

        except Exception as e:
            print(f'error from api: {e}')
            return {'error': 'Failed to add customer'}, 500


