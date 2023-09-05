from models import  db 
from app import app



def kill_db():
    '''
    this function drops the database
    '''
    db.drop_all()
    print('db killed')


try:

    with app.app_context():
            kill_db()

except Exception as e:
    print(e)




