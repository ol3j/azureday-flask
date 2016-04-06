from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Sequence, String, DateTime
import urllib.parse
from datetime import datetime
import os


engine = locals().get('engine', None)
Session = locals().get('Session', None)
Base = locals().get('Base', None)
initialized = locals().get('initialized', False)

env_vars = {
    'db_name': os.environ['DB_NAME'],
    'db_user': os.environ['DB_USER'],
    'db_pass': os.environ['DB_PASS'],
    'db_server': os.environ['DB_SERVER']
}

db_name = env_vars['db_name']
db_user = env_vars['db_user']
db_pass = env_vars['db_pass']
db_server = env_vars['db_server']


db_odbc = 'DRIVER={{SQL Server Native Client 11.0}};SERVER=tcp:{}.database.windows.net;PORT=1433;DATABASE={};UID={};PWD={};MARS_Connection=yes;'.format(db_server, db_name, db_user, db_pass)


# connect to DB
if not engine:
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(
        urllib.parse.quote_plus(db_odbc), pool_recycle=3600)
    )
if not Session:
    Session = sessionmaker(bind=engine)
if not Base:
    Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, Sequence('check_id_seq'), primary_key=True, index=True)
    date_time = Column(DateTime, default=datetime.utcnow)
    suffix = Column(String(255), nullable=False, index=True, default='suffix')
    mobile = Column(String(255), nullable=False, index=True, default='mobile')
    image = Column(String(255), nullable=False, index=True, default='image')


Base.metadata.create_all(engine)
