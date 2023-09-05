#app.py
from flask import Flask, jsonify, session
from models import db
from flask_login import LoginManager
from models import Country, Customer, User, Administrator, AirlineCompany, Ticket, UserRole, Flight
from datetime import datetime, timedelta
from flask import request
from flask_restful import Api, Resource
from flight_api import FlightResource, FlightByParamsResource, GetMyFlightsResource
from airline_api import AirlineResource
from login_api import LoginResource, LogoutResource
from country_api import CountryResource
from user_api import CreateUserResource
from customer_api import CustomerResource
from ticket_api import TicketResource
from facades import FacadeBase, AirlineFacade, AnonymousFacade, AdministratorFacade, CustomerFacade
from passlib.hash import sha256_crypt
from facades import LoginToken
from flasgger import Swagger





app = Flask(__name__)
app.secret_key = 'secret_key'

## local db from docker container
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:102030@localhost:13306/EasyFly'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


username = 'root1'
password = 'EasyFlight102030'
server = 'db-easy-flight.mysql.database.azure.com'
port = 3306  
database = 'easyfly'


connection_string = f"mysql+mysqlconnector://{username}:{password}@{server}:{port}/{database}"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db.init_app(app)



@app.route('/')
def hello():
    return jsonify({'hello': {'welcome': 'easyFlight'}}), 200






api = Api(app)



facade = FacadeBase(db_session=db.session)
facade_Airline_Facade = AirlineFacade(db_session=db.session)
admin_facade =  AdministratorFacade(dal="dal", login_token='login_token')  

resource_kwargs = {
    'facade': facade,
    'facade_Airline_Facade': facade_Airline_Facade,
    'admin_facade': admin_facade

}
resource_kwargs_flight = {
    'facade': facade,
    'facade_Airline_Facade': facade_Airline_Facade,

}

customer_facade = CustomerFacade(db.session)  
api.add_resource(TicketResource, '/buy', resource_class_kwargs={'customer_facade': customer_facade})

api.add_resource(CreateUserResource, '/createUser', resource_class_kwargs={'facade': facade, 'base_facade': facade})


api.add_resource(FlightResource, '/flights', '/flights/<int:flight_id>', resource_class_kwargs=resource_kwargs_flight)
api.add_resource(FlightByParamsResource, '/flights/parameters', resource_class_kwargs={'facade': facade, 'facade_Airline_Facade': facade_Airline_Facade})
api.add_resource(GetMyFlightsResource, '/flights/airline', resource_class_kwargs={'facade': facade, 'facade_Airline_Facade': facade_Airline_Facade})

api.add_resource(AirlineResource, '/airline' ,'/airline/<int:airline_id>', resource_class_kwargs=resource_kwargs)

api.add_resource(CountryResource, '/country','/country/<int:country_id>', resource_class_kwargs=resource_kwargs_flight)

anonymous_facade = AnonymousFacade(db.session)
api.add_resource(LoginResource, '/login', resource_class_kwargs={'facade': anonymous_facade, 'anonymous_facade': anonymous_facade})
api.add_resource(LogoutResource, '/logout')


api.add_resource(CustomerResource, '/customers', '/customers/<int:customer_id>')


@app.route('/session')
def get_login_token():
    print(f'view sessiom : {session}')
    login_token = session.get('login_token')
    if login_token:
        print(login_token)
        
        return f'Login token: {login_token}, Session: {session}'


    else:
        return 'Login token not found'


swagger = Swagger(app)



@app.route('/demoData')
def create_demo_data():
    """Add the first data to the database."""

    
    try:
          country1 = Country(name='UK', picture="path/pic1.png")
          country2 = Country(name='Israel', picture="path/pic2.png")
          country3 = Country(name='France', picture="path/pic3.png")

          db.session.add(country1)
          db.session.add(country2)
          db.session.add(country3)

          db.session.commit()
          print("contries added")
        
        # Create  roles
          admin_role = UserRole(role_name='Administrator')
          user_role = UserRole(role_name='User')
          airLine_role = UserRole(role_name='Air Line Company')

          db.session.add_all([admin_role, user_role, airLine_role])
          db.session.commit()
          print("roles  added")

          admin_password = sha256_crypt.hash("admin")
          user_password = sha256_crypt.hash("user")
          elAlPassword = sha256_crypt.hash("Amir_ElAl")
          airFrancePassword = sha256_crypt.hash("mary_france")
          dev_password = sha256_crypt.hash("123456")

          dev = User(username='yoni', password=dev_password, email='yon@mail.com', user_role_id=admin_role.id)
          admin_user = User(username='admin', password=admin_password, email='admin@mail.com', user_role_id=admin_role.id)
          user = User(username='user', password=user_password, email='user@admin.com', user_role_id=user_role.id)
          elal_user = User(username='Amir_ElAl', password=elAlPassword, email='Amir@ElAl.com', user_role_id=airLine_role.id)
          airFrance_user = User(username='mary_france', password=airFrancePassword, email='mary@flight.com', user_role_id=airLine_role.id)
          db.session.add_all([admin_user, user, elal_user, airFrance_user, dev])
          db.session.commit()
          print("users added")

 
          # Create demo  airline companies 
          airline1 = AirlineCompany(name='Air France', country=country3, user_id=airFrance_user.id)
          airline2 = AirlineCompany(name='El Al', country=country2, user_id=elal_user.id)
          db.session.add_all([airline1, airline2])
          db.session.commit()
          print("airlines added")

        

          # Create demo admins
          admin1 = Administrator(first_name='admin', last_name='admin', user=admin_user)
          admin2 = Administrator(first_name='yoni', last_name='shalfi', user=dev)
          db.session.add_all([admin1, admin2])
          db.session.commit()
          print("admins added")



          alice_card = sha256_crypt.hash("1111-2222-3333-4444")
          yoni_card = sha256_crypt.hash("5555-6666-7777-8888")

          # Create demo customers
          customer1 = Customer(first_name='Alice', last_name='Johnson', address='123 Main St', phone_no='555-1234', credit_card_no=alice_card, user=user)
          customer2 = Customer(first_name='yoni', last_name='shalfi', address='israel street', phone_no='555-5678', credit_card_no=yoni_card, user=dev)
          db.session.add_all([customer1, customer2])
          db.session.commit()
          print("customers added")


          # Create demo flights
          flight1 = Flight(airline_company=airline1, origin_country=country1, destination_country=country2, departure_time=datetime.now(), landing_time=datetime.now() + timedelta(hours=2), remaining_Tickets=100)
          flight2 = Flight(airline_company=airline2, origin_country=country1, destination_country=country3, departure_time=datetime.now(), landing_time=datetime.now() + timedelta(hours=2), remaining_Tickets=200)
          flight3 = Flight(airline_company=airline1, origin_country=country3, destination_country=country1, departure_time=datetime.now(), landing_time=datetime.now() + timedelta(hours=2), remaining_Tickets=100)
          flight4 = Flight(airline_company=airline2, origin_country=country2, destination_country=country3, departure_time=datetime.now(), landing_time=datetime.now() + timedelta(hours=2), remaining_Tickets=200)


          db.session.add_all([flight1, flight2, flight3, flight4])
          db.session.commit()
          print("Flights added")


          # Create demo tickets
          ticket1 = Ticket(flight=flight1, customer=customer1, tickets_number=1, booking_code = 'AA12345')
          ticket2 = Ticket(flight=flight2, customer=customer2, tickets_number=2, booking_code='XX12345')
          db.session.add_all([ticket1, ticket2])
          db.session.commit()
          print("tickets added")

          return jsonify("data added")
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while creating demo data'})



# if __name__ == '__main__':
#     with app.app_context():
#          db.create_all()
         
    
#     app.run(debug=True)


