from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite veritabanı dosyası için bir engine oluşturun
engine = create_engine('sqlite:///user.db', echo=True)  # my_database.db adında bir dosya oluşturur

# Base sınıfını tanımlayın
Base = declarative_base()

# Veritabanı işlemleri için bir Session sınıfı oluşturun
Session = sessionmaker(bind=engine)

# Base sınıfını kullanarak tabloları tanımlayın
class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)
    user_surname = Column(String)
    user_phone = Column(Integer)
    user_department = Column(String)
    user_permission = Column(Integer)
    user_picture = Column() #TODO find a way to restore image data in sqllite

# Veritabanı tablolarını oluşturun (eğer yoksa)
Base.metadata.create_all(engine)
