
#facades.py
from dal import DAL
from logger_config import logger
from flask import jsonify, session, json

from models import( db,
Country,Customer, User, Administrator,AirlineCompany,Ticket,UserRole,Flight)

from dal import DAL
from datetime import datetime
from  flask_restful import marshal
from sqlalchemy.orm import aliased
from datetime import datetime
from collections import OrderedDict
from sqlalchemy.orm import joinedload


db_session = db.session
dal = DAL(db_session)


class LoginToken:
    def __init__(self, id, name, role, user, air_line_company_id=None, customer_id=None):
        self.id = id
        self.name = name
        self.role = role
        self.user = user
        self.air_line_company_id = air_line_company_id
        self.customer_id = customer_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'user': self.user.id,
            'air_line_company_id': self.air_line_company_id,
            'customer_id': self.customer_id
        }


class FacadeBase:
    def __init__(self, db_session):
        self.dal = DAL(db_session)

    def get_all_flights(self):  
        try:
            flights = self.dal.get_all(Flight)
            logger.info('Fetched all flights')
            print(f'quried from facades : {[flight.to_dict() for flight in flights]}')
            return [flight.to_dict() for flight in flights], 200
        except Exception as e:
            logger.error('Error fetching flights: %s', e)
            return {'error': 'Error fetching flights'}, 500


    def get_flight_by_id(self, flight_id):
        try:
            flight = self.dal.get_by_id(Flight, flight_id)
            if flight:
                logger.info('Fetched flight with id %s', flight_id)
                print(f'quried from facades : {flight.to_dict()}')

                return flight.to_dict(), 200
            else:
                logger.info('Flight not found with id %s', flight_id)
                return {'error': 'Flight not found'}, 404
        except Exception as e:
            logger.error('Error fetching flight by id: %s', e)
            return {'error': 'Error fetching flight by id'}, 500



    def get_flights_by_parameters(self, flight_fields, **parameters):
        try:
            print("Received parameters:", parameters)

            if 'origin_country__name' in parameters:
                origin_country_name = parameters.pop('origin_country__name')
                origin_country = Country.query.filter_by(name=origin_country_name).first()
                if origin_country:
                    parameters['origin_country_id'] = origin_country.id

            if 'destination_country__name' in parameters:
                destination_country_name = parameters.pop('destination_country__name')
                destination_country = Country.query.filter_by(name=destination_country_name).first()
                if destination_country:
                    parameters['destination_country_id'] = destination_country.id

            if 'airline_company__name' in parameters:
                airline_company_name = parameters.pop('airline_company__name')
                airline_company = AirlineCompany.query.filter_by(name=airline_company_name).first()
                if airline_company:
                    parameters['airline_company_id'] = airline_company.id

            flights = self.dal.get_by_parameters(Flight, **parameters)
            
            return [flight.to_dict() for flight in flights]

        except Exception as e:
            print("Exception:", e)
            return jsonify({'error': 'Invalid request'}), 400






    def get_all_airlines(self):
        try:
            airlines = self.dal.get_all(AirlineCompany)
            logger.info('Fetched all airlines')
            print(f'queried from facade: {[airline.to_dict() for airline in airlines]}')
            return jsonify([airline.to_dict() for airline in airlines]), 200
        
        except Exception as e:
            logger.error('Error fetching airlines: %s', e)
            return jsonify({'error': 'Error fetching airlines'}), 500

    def get_airline_by_id(self, id):
        try:
            airline = self.dal.get_by_id(AirlineCompany, id)
            if airline:
                logger.info('Fetched airline with id %s', id)
                print(f'queried from facade:{airline.to_dict()}')
                return jsonify(airline.to_dict()), 200
            else:
                return jsonify({'error': 'Airline not found'}), 404
        except Exception as e:
            logger.error('Error fetching airline by id: %s', e)
            return jsonify({'error': 'Error fetching airline by id'}), 500
        
    def get_airline_by_name(self, name):
        raise NotADirectoryError


    def get_all_countries(self):
            try:
                countries = self.dal.get_all(Country)
                logger.info('Fetched all countries')
                return jsonify([country.to_dict() for country in countries]), 200
            except Exception as e:
                logger.error('Error fetching countries: %s', e)
                return jsonify( {'error': 'Error fetching countries'}), 500
            
    def get_country_by_id(self, id):
        try:
            country = self.dal.get_by_id(Country, id)
            if country:
                logger.info('Fetched country with id %s', id)
                return jsonify(country.to_dict()), 200
            else:
                return jsonify({'error': 'Country not found'}), 404
        except Exception as e:
            logger.error('Error fetching country by id: %s', e)
            return jsonify({'error': 'Error fetching country by id'}), 500
        

    def create_new_user(self, username, password, email, user_role_id=2 ):
        try:
            user = User(username=username, email=email, user_role_id=user_role_id)
            user.set_password(password)
            self.dal.add(user)
            self.dal.update()
            logger.info('Created new user %s', user)
            return user.to_dict()  
        except Exception as e:
            logger.error('Error creating new user: %s', e)
            return {'error': 'Error creating new user'}
        

    def create_new_user_with_customer(self, username, password, email):
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            self.dal.add(user)
            self.dal.update()
            logger.info('Created new user %s', user)
            return user
        except Exception as e:
            logger.error('Error creating new user: %s', e)
            return {'error': 'Error creating new user'}

class AnonymousFacade(FacadeBase):
    def __init__(self, db_session, login_token=None):
        super().__init__(db_session)
        self._login_token = login_token

    @property
    def login_token(self):
        return self._login_token


    def login(self, username, password):
        user = self.dal.get_user_by_username(username)

        if user and user.check_password(password):
            role = user.user_role_relationship.role_name
            air_line_company_id = None
            customer_id = None

            customer_id = user.customer_relationship.id if user.customer_relationship else None

            if role == 'Air Line Company' and user.airline_company_relationship:
                air_line_company_id = user.airline_company_relationship[0].id if user.airline_company_relationship else None

            login_token = LoginToken(
                id=user.id, 
                name=user.username, 
                role=role, 
                user=user, 
                air_line_company_id=air_line_company_id,
                customer_id=customer_id
            )

            print(f"LoginToken created: {login_token.to_dict()}") 
            token_dict = login_token.to_dict()
            
            session['login_token'] = token_dict
            print(f'session = {session}')

            #  facade return based on role
            if role == 'User':
                return CustomerFacade(self.dal, login_token)
            elif role == 'Air Line Company':
                return AirlineFacade(self.dal, login_token)
            elif role == 'Administrator':
                return AdministratorFacade(self.dal, login_token)
            else:
                raise ValueError(f"Unexpected role: {role}")

        else:
            raise ValueError("Invalid credentials")


    def logout():
        try:
            session.pop('login_token', None)
            return jsonify('logged out : ok', 200)

        except Exception as e:
            logger.error (f'cant log out: {e}')
            return jsonify('error : please double check that you singed-in')




    def add_customer(self, first_name, last_name, address, phone_no, credit_card_num, username, password, email):
        try:
            print("Inside add_customer - Before get_user_by_username")
            user = self.dal.get_user_by_username(username)
            print("User retrieved:", user)
            
            if not user:
                print("Creating new user...")
                user = self.create_new_user_with_customer(username, password, email)
                self.dal.add(user)  
                self.dal.update()


            print("Creating customer...")

            customer = Customer(first_name=first_name, last_name=last_name, address=address, phone_no=phone_no,
                                credit_card_no=None, user=user)
            customer.credit_card_no =customer.hash_credit_card(credit_card_num)



            print(f'customer data : {customer}')
            self.dal.add(customer)
            logger.info('Customer added: %s', customer)
            return customer.to_dict()
        
        except Exception as e:
            logger.error('Error adding customer: %s', e)
            return {'error': 'Error adding customer'}, 500



class CustomerFacade(AnonymousFacade):
    
    def to_dict(self):
        return {
            'user_id': self.login_token.id,
            'username': self.login_token.name,
            'role': self.login_token.role
        }


    def update_customer(self, user_name, data):
        try:
            user = self.dal.get_user_by_username(user_name)
            if user and user.customer:
                customers = user.customer  

                print(f'do I have customer(s)?: {customers}')

                print(f'Type of customers: {type(customers)}')

                for customer in customers:
                    if 'first_name' in data:
                        customer.first_name = data['first_name']
                    if 'last_name' in data:
                        customer.last_name = data['last_name']
                    if 'address' in data:
                        customer.address = data['address']
                    if 'phone_no' in data:
                        customer.phone_no = data['phone_no']
                    if 'credit_card_no' in data:
                        hashed_credit_card = customer.hash_credit_card(data['credit_card_no'])
                        customer.credit_card_no = hashed_credit_card

                self.dal.update()
                logger.info('Customers updated successfully')
                return customers, 200
            else:
                return {'error': 'User not found or has no associated customer record'}, 404

        except ValueError as e:
            logger.error('Customers update failed: %s', e)
            return {'error': 'Customers update failed'}, 403


    def add_ticket(self, flight_id, credit_card, tickets_number=1):
        try:
            flight = self.dal.get_by_id(Flight, flight_id)

            login_token = session.get('login_token')
            if login_token is None:
                raise ValueError("User not logged in or session expired.")
            
            customer_id = login_token.get('customer_id')
            if not customer_id:
                raise ValueError("No customer ID found in session.")
            

            customer = self.dal.get_by_id(Customer, customer_id)
            db_credit_card = customer.credit_card_no
            is_valid_card =  customer.check_credit_card(credit_card)
          
            if not is_valid_card:
                raise ValueError("The provided credit card is invalid.")


            if flight.remaining_Tickets >= tickets_number:
                booking_code = Ticket.generate_unique_booking_code()  
                ticket = Ticket(
                    flight_id=flight_id,
                    customer_id=customer_id,
                    tickets_number=tickets_number,
                    booking_code=booking_code)
                
              
                self.dal.add(ticket)
                flight.remaining_Tickets -= tickets_number  
                self.dal.update()
                logger.info('Ticket added successfully')
                return ticket.to_dict()
            else:
                raise ValueError("Not enough remaining tickets")
                
        except ValueError as e:
            logger.error('Ticket add failed: %s', e)
            return {'error': 'Ticket add failed'}, 400
                    

    def get_my_tickets(self):
        try:
            login_token = session.get('login_token')
            customer_id = login_token['customer_id']
            tickets = self.dal.get_flights_by_customer(customer_id)

            logger.info('Fetched tickets for customer :%s', customer_id)
            return [ticket.to_dict() for ticket in tickets], 200
        except Exception as e:
            logger.error('Error fetching tickets: %s', e)
            return jsonify({'error': 'Error fetching tickets'}), 500
        

    def remove_ticket(self, booking_code):
        try:
            ticket = self.dal.get_ticket_by_booking_code(booking_code)
            
            if not ticket:
                raise ValueError(f"No ticket found with booking code: {booking_code}")

            self.dal.remove(ticket)

            flight = self.dal.get_by_id(Flight, ticket.flight_id)
            flight.remaining_Tickets += ticket.tickets_number
            self.dal.update()

            logger.info(f'Ticket with booking code {booking_code} removed successfully')
            return {'message': 'Ticket removed successfully'}, 200

        except ValueError as e:
            logger.error('Error removing ticket: %s', e)
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error('Unexpected error removing ticket: %s', e)
            return {'error': 'Unexpected error while removing ticket'}, 500



class AirlineFacade(AnonymousFacade):

    def to_dict(self):
        return {
            'id': self._login_token.id,
            'username': self._login_token.name,
            'role': self._login_token.role
        }

    
    def get_my_flights(self):
        model = Flight
        session_data = session.get('login_token')
        id = session_data.get('air_line_company_id')

        try:
            flights = self.dal.get_by_id_all(model=model, id=id)
            logger.info('Fetched flights for airline id: %s', id)
            return flights
        except Exception as e:
            logger.error('Error fetching flights: %s', e)
            return jsonify({'error': 'Error fetching flights'}), 500


    def update_airline(self, name):
        try:
            session_data = session.get('login_token')
            id = session_data.get('air_line_company_id')

            company = self.dal.get_by_id(AirlineCompany, id) 

            if company:
                try:
                    company.name = name

                except Exception as e:
                    logger.error(e)
                    return('please provide an company data (name only)')

                self.dal.update()
                logger.info('Updated airline id: %s', id)
                return {'message': 'Airline updated'}, 200
            else:
                raise ValueError("Unauthorized")  
            
        except ValueError as e:
            logger.error('Error updating airline: %s', e)
            return jsonify({'error': 'Error updating airline'}), 400



    def add_flight(self, departure_time, landing_time, origin_country_id, destination_country_id, remaining_tickets, airline_company_id):
        try:
            if departure_time > landing_time or origin_country_id == destination_country_id:
                raise ValueError("Invalid flight parameters")
            flight = Flight(departure_time=departure_time, landing_time=landing_time, origin_country_id=origin_country_id,
                            destination_country_id=destination_country_id, remaining_Tickets=remaining_tickets,
                            airline_company_id=airline_company_id)
            self.dal.add(flight)
            logger.info('Added flight with id: %s for airline id: %s', flight.id, airline_company_id)
            return jsonify(flight.to_dict()), 201
        except ValueError as e:
            logger.error('Error adding flight: %s', e)
            print(f'error from facade = {e}')
            return jsonify({'error': 'Error adding flight'}), 400



    def update_flight(self, flight_id, data):
        try:
            flight = self.dal.get_by_id(Flight, flight_id)
            if flight is None:
                return jsonify({'error': 'Flight not found'}), 404

            if 'login_token' not in session:
                print("Unauthorized: No login_token in session")
                return jsonify({'error': 'Unauthorized access'}), 403

            login_token = session['login_token']
            print("login_token.id:", login_token.get('id'))
            print("flight.airline_company_id:", flight.airline_company_id)

            if login_token.get('role') != 'Air Line Company':
                print("Unauthorized: ID mismatch")
                return jsonify({'error': 'Unauthorized access'}), 403

            if 'departure_time' in data:
                flight.departure_time = data['departure_time']
            if 'landing_time' in data:
                flight.landing_time = data['landing_time']
            if 'origin_country_id' in data:
                flight.origin_country_id = data['origin_country_id']
            if 'destination_country_id' in data:
                flight.destination_country_id = data['destination_country_id']
            if 'remaining_tickets' in data:
                flight.remaining_Tickets = data['remaining_tickets']

            self.dal.update()
            logger.info('Updated flight id: %s', flight.id)
            return jsonify(flight.to_dict()), 200

        except ValueError as e:
            logger.error('Error updating flight: %s', e)
            return jsonify({'error': 'Error updating flight'}), 400





    def remove_flight(self, flight_id):
        try:
            flight = self.dal.get_by_id(Flight, flight_id)
            if flight is None:
                return jsonify({'error': 'Flight not found'}), 404

            if 'login_token' not in session:
                return jsonify({'error': 'Unauthorized access'}), 403

            login_token = session['login_token']
            if login_token.get('role') == 'User':
                return jsonify({'error': 'Unauthorized access'}), 403

            self.dal.remove(flight)
            logger.info('Removed flight id: %s', flight_id)
            return jsonify({'message': 'Flight removed'}), 200

        except Exception as e:
            logger.error('Error removing flight: %s', e)
            return jsonify({'error': 'Error removing flight'}), 400




class AdministratorFacade(AnonymousFacade):
    

    def __init__(self, dal, login_token):
        super().__init__(dal)
        self._login_token = login_token

    def to_dict(self):
        return {
            'id': self._login_token.id,
            'username': self._login_token.name,
            'role': self._login_token.role
        }
    
    
    def get_all_customers(self):
        try:
            if 'login_token' not in session:
                print("Unauthorized: No login_token in session")
                return jsonify({'error': 'Unauthorized access'}), 403

            login_token = session['login_token']
            print("login_token.role:", login_token.get('role'))

            if login_token.get('role') != 'Administrator':
                print("Unauthorized: Role mismatch")
                return jsonify({'error': 'Unauthorized access'}), 403

            customers = self.dal.get_all(Customer)
            logger.info('Fetched all customers')
            return jsonify([customer.to_dict() for customer in customers]), 200
        except Exception as e:
            logger.error('Error fetching customers: %s', e)
            return jsonify({'error': 'Error fetching customers'}), 500

        
    def get_customer_by_id(self, id):
        try:
            if 'login_token' not in session:
                print("Unauthorized: No login_token in session")
                return jsonify({'error': 'Unauthorized access'}), 403

            login_token = session['login_token']
            print("login_token.role:", login_token.get('role'))

            if login_token.get('role') != 'Administrator':
                print("Unauthorized: Role mismatch")
                return jsonify({'error': 'Unauthorized access'}), 403

            customer = self.dal.get_by_id(Customer, id)
            if customer:
                logger.info('Fetched Customer with id %s', id)
                print(f'queried from facade: {customer.to_dict()}')
                return jsonify(customer.to_dict()), 200
            else:
                return jsonify({'error': 'Customer not found'}), 404
        except Exception as e:
            logger.error('Error fetching Customer by id: %s', e)
            return jsonify({'error': 'Error fetching Customer by id'}), 500
            

    def add_airline(self, name, country_id):
            try:
                airline = AirlineCompany(name=name, country_id=country_id)
                self.dal.add(airline)
                logger.info('Added new airline: %s', name)
                return jsonify(airline.to_dict()), 201
            except Exception as e:
                logger.error('Error adding airline: %s', e)
                return jsonify({'error': 'Error adding airline'}), 500
            
    def remove_airline(self, airline_id):
        if not airline_id:
            return {'error': 'Airline ID is required'}, 400 
        
        try:
            airline = self.dal.get_by_id(AirlineCompany, airline_id)
            if airline:
                self.dal.remove(airline)
                logger.info('Removed airline with id: %s', airline_id)
                return jsonify({'success': 'Airline removed'}), 200
            else:
                return jsonify({'error': 'Airline not found'}), 404
        except Exception as e:
            logger.error('Error removing airline: %s', e)
            return jsonify({'error': 'Error removing airline'}), 500


    def remove_customer(self, customer_id):
        try:
            customer = self.dal.get_by_id(Customer, customer_id)
            if customer:
                self.dal.remove(customer)
                logger.info('Removed customer with id: %s', customer_id)
                return {'success': 'Customer removed'}, 200
            else:
                return {'error': 'Customer not found'}, 404
        except Exception as e:
            logger.error('Error removing customer: %s', e)
            return {'error': 'Error removing customer'}, 500
            

    def update_airline(self, airline_id, name=None, country_id=None):
        try:
            airline = self.dal.get_by_id(AirlineCompany, airline_id)
            if not airline:
                return {'error': 'Airline not found'}, 404

            if name:
                airline.name = name
            if country_id:
                airline.country_id = country_id

            self.dal.update() 

            logger.info('Updated airline ID %d: %s', airline_id, name)
            return airline.to_dict()
        except Exception as e:
            logger.error('Error updating airline ID %d: %s', airline_id, e)
            return jsonify ({'error' : e})









