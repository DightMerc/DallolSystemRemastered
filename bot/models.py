from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    status = Column(String)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


    def __repr__(self):
       return "<User(id='%s', chat_id='%s', role='%s')>" % (
                            self.id, self.chat_id, self.role)

class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)

    def __repr__(self):
       return "<Region(id='%s', parent_id='%s')>" % (
                            self.id, self.parent_id)

class RegionTranslation(Base):
    __tablename__ = 'region_translations'

    id = Column(Integer, primary_key=True)
    locale = Column(String)
    region_id = Column(Integer)
    name = Column(String)

    def __repr__(self):
       return "<Region(id='%s', name='%s')>" % (
                            self.id, self.name)

class STUDENT(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    city = Column(String)
    date_birth = Column(DateTime, default=datetime.datetime.utcnow)
    date_start = Column(DateTime, default=datetime.datetime.utcnow)

    stud_id = Column(Integer, ForeignKey('study.id'),
        nullable=False)


    def __repr__(self):
       return "<Region(id='%s')>" % (
                            self.id)

class FAK(Base):
    __tablename__ = 'fak'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    head = Column(String)
    count = Column(Integer)

    fak = Column(Integer, ForeignKey('study.id'),
        nullable=False)

    def __repr__(self):
       return "<Region(id='%s', name='%s')>" % (
                            self.id, self.name)

class STUDY(Base):
    __tablename__ = 'study'

    id = Column(Integer, primary_key=True)
    stud_id = relationship("STUDENT")
    fak_id = relationship("FAK")
    speciality = Column(String)
    group = Column(String)
    year = Column(DateTime, default=datetime.datetime.utcnow)
    price = Column(Integer)

    def __repr__(self):
       return "<Region(id='%s')>" % (
                            self.id)
