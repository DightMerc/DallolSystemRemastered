import datetime

import sqlalchemy
import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


def connect():
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format("postgres", "secret", "185.159.129.94", "5432", "dallolcrm_db")

    # The return value of create_engine() is our connection object
    engine = sqlalchemy.create_engine(url, client_encoding='utf8')

    return engine

    
print("Client connecting...", end=" ")

engine = connect()

Session = sessionmaker(bind=engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

print("Connected")

def TEST():
    q = session.query(models.STUDENT.fullname).order_by(models.STUDY.fak_id).order_by(models.STUDY.group).count()
    print(f"\n\n{str(q.statement.compile(dialect=postgresql.dialect()))}\n\n")


def CreateNewUser(user):

    if session.query(models.User).filter(models.User.chat_id==int(user)).count()!=0:
        pass
    else:
        try:
            newUser = models.User()
            newUser.chat_id =  int(user)
            newUser.status = "active"
            newUser.role = "user"

            session.add(newUser)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


def GetMainRegions(lan):
    rows = session.query(models.Region).filter(models.Region.parent_id == None).all()

    regions = []
    for row in rows:

        translation = session.query(models.RegionTranslation).filter(models.RegionTranslation.region_id==row.id, models.RegionTranslation.locale==lan).first()

        region = {
            "id": row.id,
            "name": translation.name,
            "parent_id": row.parent_id,

        }
        regions.append(region)

    return regions


def GetChildRegion(main, lan):
    current = session.query(models.RegionTranslation).filter(models.RegionTranslation.name == main).first()

    rows = session.query(models.Region).filter(models.Region.parent_id == current.region_id).all()

    regions = []
    for row in rows:
        try:
            translation = session.query(models.RegionTranslation).filter(models.RegionTranslation.region_id==row.id, models.RegionTranslation.locale==lan).first()

            region = {
                "id": row.id,
                "name": translation.name,
                "parent_id": row.parent_id,

            }
            regions.append(region)
        except Exception as e:
            pass
    
    return regions


if __name__ == "__main__":
    TEST()
    