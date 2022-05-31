from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    # --- LOGGING SENSORS / ACTUATORS ---
    @staticmethod
    def insert_magnet_value(status, beschrijving):
        sql = "INSERT INTO historiek(actiedatum, waarde, commentaar, DeviceID, ActieID) VALUES(now(), %s, %s, 14, 5)"
        params = [status, beschrijving]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_rfid_value(status, beschrijving):
        sql = "INSERT INTO historiek(actiedatum, waarde, commentaar, DeviceID, ActieID) VALUES(now(), %s, %s, 7, 6)"
        params = [status, beschrijving]
        return Database.execute_sql(sql, params)

    # --- Mailbox Events ---
    @staticmethod
    def read_sensor_gesch():
        sql = "SELECT * from brievenbusevent order by date DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensor_gesch_today():
        sql = "select * from brievenbusevent where cast(date as Date) = cast(now() as Date) order by date DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_brieven_today():
        sql = "select count(*) from brievenbusevent where cast(date as Date) = cast(now() as Date) and actieID = 3"
        return Database.get_rows(sql)

    @staticmethod
    def read_latest_lid():
        sql = "select * from brievenbusevent where cast(date as Date) = cast(now() as Date) order by date DESC LIMIT 1"
        return Database.get_one_row(sql)

    @staticmethod
    def insert_lid(status, beschrijving):
        sql = "INSERT INTO brievenbusevent(gebruikersid, actieid, date, opmerking, waarde) VALUES(null, 5, now(), %s, %s)"
        params = [beschrijving, status]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_box_site(status, beschrijving):
        sql = "INSERT INTO brievenbusevent(gebruikersid, actieid, date, opmerking, waarde) VALUES(null, 7, now(), %s, %s)"
        params = [beschrijving, status]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_box_scanner(parid, beschrijving):
        sql = "INSERT INTO brievenbusevent(gebruikersid, actieid, date, opmerking, waarde) VALUES( (Select gebruikersID from gebruiker where rfid_code like %s) , 7, now(), %s, null)"
        params = [parid, beschrijving]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_users():
        sql = "SELECT * FROM projectonedb.gebruiker"
        return Database.get_rows(sql)

    @staticmethod
    def read_user(userID):
        sql = "SELECT * FROM projectonedb.gebruiker where gebruikersID = %s"
        params = [userID]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_user(rfid, naam, pswrd, gebruikersid):
        sql = "UPDATE gebruiker SET rfid_code = %s, naam = %s, wachtwoord = %s WHERE gebruikersID = %s"
        params = [rfid, naam, pswrd, gebruikersid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_user(rfid, naam, pswrd):
        sql = "insert into gebruiker (naam, wachtwoord, rfid_code) Select %s, %s, %s Where not exists(select * from gebruiker where rfid_code=%s)"
        params = [naam, pswrd, rfid, rfid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def remove_user(id):
        sql = "DELETE FROM gebruiker WHERE gebruikersID = %s;"
        params = [id]
        return Database.execute_sql(sql, params)
