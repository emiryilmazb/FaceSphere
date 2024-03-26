from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    phone = Column(String)
    department = Column(String)
    permission = Column(String)
    photos = relationship("Photo", back_populates="user")


class Photo(Base):
    __tablename__ = 'photo'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))  # Update table name here
    file_path = Column(String)
    user = relationship("User", back_populates="photo")

class Attendence(Base):
    __tablename__ = 'attendence'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    entry_time = Column(DateTime)
    leave_time = Column(DateTime)
    user = relationship("User", back_populates="attendence")
# Veritabanı dosyasının konumu
db_path = 'sqlite:///user_database.db'
engine = create_engine(db_path)

# Veritabanını oluştur
Base.metadata.create_all(engine)
