
#models.py
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
import random
import string
db = SQLAlchemy()

class Flight(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    airline_company_id = db.Column(db.BigInteger, db.ForeignKey('airline_company.id', ondelete='CASCADE'))
    origin_country_id = db.Column(db.Integer, db.ForeignKey('country.id', ondelete='CASCADE'))
    destination_country_id = db.Column(db.Integer, db.ForeignKey('country.id', ondelete='CASCADE'))
    departure_time = db.Column(db.DateTime, nullable=False)
    landing_time = db.Column(db.DateTime, nullable=False)
    remaining_Tickets = db.Column(db.Integer, nullable=False)
    ticket_price = db.Column(db.Float, nullable=False, default=100.0) 

    airline_company = db.relationship('AirlineCompany', backref=db.backref('flights', cascade="all, delete-orphan"))

    origin_country = db.relationship('Country', foreign_keys=[origin_country_id], backref=db.backref('flights_origin', cascade="all, delete-orphan"))
    destination_country = db.relationship('Country', foreign_keys=[destination_country_id], backref=db.backref('flights_destination', cascade="all, delete-orphan"))

    flight_tickets  = db.relationship('Ticket', backref='flight', single_parent=True, cascade="all, delete-orphan")
    
    def __prep__(self):
        current_time = datetime.now()
        self.next_12_hours = current_time + timedelta(hours=12)


    def format_datetime(self, dt):
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.isoformat() if dt else None


    def to_dict(self):
        return {
            'id': self.id,
            'airline_company': {
                'id': self.airline_company.id,
                'name': self.airline_company.name
            } if self.airline_company else None,
            'origin_country': {
                'id': self.origin_country.id,
                'name': self.origin_country.name
            } if self.origin_country else None,
            'destination_country': {
                'id': self.destination_country.id,
                'name': self.destination_country.name
            } if self.destination_country else None,
            'departure_time': self.departure_time.strftime('%Y-%m-%d %H:%M') if self.departure_time else None,
            'landing_time': self.landing_time.strftime('%Y-%m-%d %H:%M') if self.landing_time else None,
            'remaining_Tickets': self.remaining_Tickets
        }
    

    def to_dict_by_params(self, parameters):
        flight_dict = {
            'id': self.id,
            'departure_time': self.departure_time.strftime('%Y-%m-%d %H:%M:%S'),
            'landing_time': self.landing_time.strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_tickets': self.remaining_Tickets,
            "remaining_Tickets": self.remaining_Tickets
        }
        
        if 'include_airline' in parameters:
            flight_dict['airline_company'] = self.airline_company.name
        
        if 'include_origin_country' in parameters:
            flight_dict['origin_country'] = self.origin_country.name
        
        if 'include_destination_country' in parameters:
            flight_dict['destination_country'] = self.destination_country.name
        
        return flight_dict





    def get_flights_by_airline_id(self, airline_company_id):
        return Flight.query.filter_by(airline_company_id=airline_company_id).all()

    
    def get_arrival_flights(self, destination_country_id):
        return Flight.query.filter_by(destination_country_id=destination_country_id).filter(Flight.landing_time <= self.next_12_hours).all()

    def get_departure_flights(self, origin_country_id):
        return Flight.query.filter_by(origin_country_id=origin_country_id).filter(Flight.departure_time <= self.next_12_hours).all()

    def get_flights_by_parameters(self, origin_country_id, destination_country_id, departure_time, landing_time):
            return Flight.query.filter(
                Flight.origin_country_id == origin_country_id,
                Flight.destination_country_id == destination_country_id,
                Flight.departure_time >= departure_time,
                Flight.landing_time <= landing_time
            ).all()
    



class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    picture = db.Column(db.String(512), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "country_name": self.name,
            'picture' : self.picture
                }

    def add_image(self, country_code):
        picture_from_api = f"www.countryflagicons.com/SHINY/64/{country_code}.png"
        self.picture = picture_from_api

        return picture_from_api







class Ticket(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    flight_id = db.Column(db.BigInteger, db.ForeignKey('flight.id', ondelete='CASCADE'))
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customer.id', ondelete='CASCADE'))
    tickets_number = db.Column(db.Integer, nullable=False, default=1)
    booking_code  = db.Column(db.String(7), unique=True, nullable=False)  

    customer = db.relationship('Customer', backref=db.backref('tickets', cascade="all, delete-orphan"), single_parent=True)
    
    __table_args__ = (
            db.UniqueConstraint('flight_id', 'customer_id', name='uq_ticket_flight_customer'),
        )
    
    @staticmethod
    def generate_unique_booking_code():
        while True:
            letters = random.choices(string.ascii_uppercase, k=2)
            numbers = random.choices(string.digits, k=5)
            booking_code = ''.join(letters) + ''.join(numbers)
            
           
            existing_code = Ticket.query.filter_by(booking_code=booking_code).first()
            if not existing_code:
                return booking_code
            
    def to_dict(self):
        return {
            "tickets_number": self.tickets_number,
            "booking_code": self.booking_code
        }





class AirlineCompany(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id', ondelete='CASCADE'))
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)

    country = db.relationship('Country', backref=db.backref('airline_companies', cascade="all, delete-orphan"))
    user_airline_company = db.relationship('User', backref='airline_company', cascade="all, delete")



    def to_dict(self):
        return {
            "id": self.id,
            "air_line_name": self.name,
            }


    def get_airline_by_username(self, username):
            airline = db.session.query(AirlineCompany).join(User).filter(User.username == username).first()
            return airline



class Customer(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone_no = db.Column(db.String(255), unique=True, nullable=False)
    credit_card_no = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)

    user_customer = db.relationship('User', backref='customer', uselist=False, cascade="all, delete")


    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'phone_no' : self.phone_no,
            'user_id' : self.user_id
            }

    def hash_credit_card(self, credit_card_no):
        return sha256_crypt.hash(credit_card_no)


    def check_credit_card(self, credit_card_no):
        return sha256_crypt.verify(credit_card_no, self.credit_card_no)

    def get_customer_by_username(self, username):
        customer = db.session.query(Customer).join(User).filter(User.username == username).first()
        return customer

    def get_tickets_by_customer(self, customer_id):
        tickets = db.session.query(Ticket).join(Customer).filter(Customer.id == customer_id).all()
        return tickets


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(255), unique=True, nullable=False)

    @staticmethod
    def get_default_user_role_id():
        default_role = UserRole.query.filter_by(role_name='user').first()
        if default_role:
            return default_role.id
        else:
            return None  
        


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete='CASCADE'), nullable=True, default=UserRole.get_default_user_role_id)

    user_role_relationship = db.relationship('UserRole', backref='users')
    customer_relationship = db.relationship('Customer', backref='user', uselist=False, cascade="all, delete-orphan")

    administrator_relationship = db.relationship('Administrator', backref='user', single_parent=True, cascade="all, delete-orphan")
    airline_company_relationship = db.relationship('AirlineCompany', backref='user', single_parent=True, cascade="all, delete-orphan")

  
    def to_dict(self):
        return {
            'username' : self.username,
            'password' : self.password,
            'email' : self.email
        }

    def set_password(self, password):
        self.password = sha256_crypt.hash(password)

    def check_password(self, password):
        return sha256_crypt.verify(password, self.password)





class Administrator(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'))

    user_relationship = db.relationship('User', backref='administrator', cascade="all, delete")




