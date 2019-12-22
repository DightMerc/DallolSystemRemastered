import psycopg2
import datetime

print("Client connected")
try:
    connection = psycopg2.connect(user = "postgres",
                                password = "secret",
                                host = "185.159.129.94",
                                port = "5432",
                                database = "dallolcrm_db")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)


def CreateNewUser(user):
    cursor = connection.cursor()

    cursor.execute(
        f"SELECT * FROM users WHERE chat_id={user}"
        )

    rows = cursor.fetchall()
    if len(rows)!=0:
        pass
    else:
        cursor.execute(
        "INSERT INTO users (chat_id, status, role, created_at) VALUES (%s, 'active', 'user', %s)", [user, datetime.datetime.now()]
        )
    connection.commit()
    cursor.close()


def GetMainRegions(lan):
    cursor = connection.cursor()

    cursor.execute(
        f"SELECT * FROM regions WHERE parent_id IS NULL"
        )

    rows = cursor.fetchall()

    regions = []
    for row in rows:
        cursor.execute(
        f"SELECT * FROM region_translations WHERE region_id='{row[0]}' AND locale='{lan}'"
        )
        region = {
            "id": row[0],
            "name": cursor.fetchone()[3],
            "parent_id": row[2],

        }
        regions.append(region)
    cursor.close()

    return regions


def GetChildRegion(main, lan):
    cursor = connection.cursor()

    cursor.execute(
        f"SELECT * FROM region_translations WHERE name='{main}'"
        )
    
    cursor.execute(
        f"SELECT * FROM regions WHERE parent_id={cursor.fetchone()[2]}"
        )

    rows = cursor.fetchall()

    regions = []
    for row in rows:
        cursor.execute(
        f"SELECT * FROM region_translations WHERE region_id='{row[0]}' AND locale='{lan}'"
        )
        region = {
            "id": row[0],
            "name": cursor.fetchone()[3],
            "parent_id": row[2],

        }
        regions.append(region)
    cursor.close()
    
    return regions


# if __name__ == "__main__":
#     GetMainRegions()
    