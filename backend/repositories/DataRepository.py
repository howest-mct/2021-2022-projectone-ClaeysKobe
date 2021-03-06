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

    @staticmethod
    def insert_ldr_values(waarde1, waarde2, waarde3, waarde4, waarde5):
        sql = "INSERT INTO historiek(actiedatum, waarde, commentaar, DeviceID, ActieID) values \
            (now(), %s, 'Veranderde ldr waarde', 1, 3),\
            (now(), %s, 'Veranderde ldr waarde', 2, 3),\
            (now(), %s, 'Veranderde ldr waarde', 3, 3),\
            (now(), %s, 'Veranderde ldr waarde', 4, 3),\
            (now(), %s, 'Veranderde ldr waarde', 5, 3)"
        params = [waarde1, waarde2, waarde3, waarde4, waarde5]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_led(value):
        sql = "insert into historiek (actiedatum, waarde, commentaar, deviceID, actieID) values (now(), %s, 'Ledstrip getoggeld', 11, 8);"
        params = [value]
        return Database.execute_sql(sql, params)

    # --- Mailbox Events ---

    @staticmethod
    def read_sensor_gesch():
        sql = "SELECT * from brievenbusevent where deleted = 0 order by date DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensor_gesch_today():
        sql = "select * from brievenbusevent where cast(date as Date) = cast(now() as Date) and deleted = 0 order by date DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_brieven_today():
        sql = "select count(*) as `Aantal` from brievenbusevent where cast(date as Date) = cast(now() as Date) and actieID = 3 and deleted = 0"
        return Database.get_rows(sql)

    @staticmethod
    def read_latest_letter():
        sql = "select * from brievenbusevent where cast(date as Date) = cast(now() as Date) and ActieID = 3 and deleted = 0 order by date DESC LIMIT 1"
        return Database.get_one_row(sql)

    @staticmethod
    def read_latest_lid():
        sql = "select * from brievenbusevent where ActieID = 5 and deleted = 0 order by date DESC LIMIT 1"
        return Database.get_one_row(sql)

    @staticmethod
    def read_latest_lock():
        sql = "select * from brievenbusevent where cast(date as Date) = cast(now() as Date) and ActieID = 7 and deleted = 0 order by date DESC LIMIT 1"
        return Database.get_one_row(sql)

    @staticmethod
    def insert_lid(status, beschrijving):
        sql = "INSERT INTO brievenbusevent(gebruikersid, actieid, date, opmerking, waarde) VALUES(null, 5, now(), %s, %s)"
        params = [beschrijving, status]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_box_site(status, beschrijving, user):
        sql = "INSERT INTO brievenbusevent(gebruikersid, actieid, date, opmerking, waarde) VALUES(%s, 7, now(), %s, %s)"
        params = [user, beschrijving, status]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_box_scanner(parid, beschrijving, waarde):
        sql = "INSERT INTO brievenbusevent(gebruikersid, actieid, date, opmerking, waarde) VALUES( (Select gebruikersID from gebruiker where rfid_code like %s) , 7, now(), %s, %s)"
        params = [parid, beschrijving, waarde]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_users():
        sql = "SELECT gebruikersID, naam, AES_DECRYPT(`wachtwoord`, 'secretsMustBeKept') AS `wachtwoord`, rfid_code, registreerdatum, email FROM projectonedb.gebruiker"
        return Database.get_rows(sql)

    @staticmethod
    def read_user(userID):
        sql = "SELECT gebruikersID, naam, AES_DECRYPT(`wachtwoord`, 'secretsMustBeKept') AS `wachtwoord`, rfid_code, registreerdatum, email FROM projectonedb.gebruiker where gebruikersID = %s"
        params = [userID]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_user(rfid, naam, pswrd, gebruikersid, email):
        sql = "UPDATE gebruiker SET rfid_code = %s, naam = %s, wachtwoord = AES_ENCRYPT(%s, 'secretsMustBeKept'), email = %s WHERE gebruikersID = %s"
        params = [rfid, naam, pswrd, email, gebruikersid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_user(rfid, naam, pswrd, email):
        sql = "insert into gebruiker (naam, wachtwoord, rfid_code, registreerdatum, email) Select %s, AES_ENCRYPT(%s, 'secretsMustBeKept'), %s, now(), %s Where not exists(select * from gebruiker where rfid_code=%s)"
        params = [naam, pswrd, rfid, email, rfid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def remove_user(id):
        sql = "DELETE FROM gebruiker WHERE gebruikersID = %s;"
        params = [id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def add_letter():
        sql = "insert into brievenbusevent (gebruikersID, ActieID, date, opmerking, waarde) values (null, 3, now(), 'New mail!', null);"
        return Database.execute_sql(sql)

    @staticmethod
    def check_rfid(rfid_code):
        sql = "SELECT naam FROM gebruiker WHERE rfid_code = %s"
        params = [rfid_code]
        return Database.get_one_row(sql, params)

    @staticmethod
    def check_gebruiker(naam, wachtwoord):
        sql = "SELECT * FROM gebruiker WHERE naam = %s and wachtwoord = AES_ENCRYPT(%s, 'secretsMustBeKept')"
        params = [naam, wachtwoord]
        return Database.get_one_row(sql, params)

    @staticmethod
    def test_gebruiker():
        sql = "SELECT AES_DECRYPT(`wachtwoord`, 'secretsMustBeKept') AS `wachtwoord` FROM `gebruiker` WHERE `rfid_code` = '55452030326'"
        return Database.get_one_row(sql)

    @staticmethod
    def truncate_events():
        sql = "UPDATE brievenbusevent set deleted = 1"
        return Database.execute_sql(sql)

    @staticmethod
    def get_latest_letters(date):
        sql = "SELECT count(*) as `Aantal` FROM brievenbusevent WHERE NOT(date > now() OR date < %s) and ActieID = 3 and deleted = 0"
        params = [date]
        return Database.get_one_row(sql, params)

    @staticmethod
    def get_id(name):
        sql = "SELECT gebruikersID FROM gebruiker WHERE naam = %s"
        params = [name]
        return Database.get_one_row(sql, params)

    @staticmethod
    def get_id_by_rfid(rfid):
        sql = "SELECT gebruikersID FROM gebruiker WHERE rfid_code = %s"
        params = [rfid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def check_name(rfid_code):
        sql = "SELECT naam FROM gebruiker WHERE gebruikersID = %s"
        params = [rfid_code]
        return Database.get_one_row(sql, params)

    @staticmethod
    def emptied_box():
        sql = "insert into brievenbusevent (gebruikersID, ActieID, date, opmerking, waarde) values (null, 9, now(), 'Emptied mailbox', null);"
        return Database.execute_sql(sql)

    @staticmethod
    def read_latest_empty():
        sql = 'SELECT date FROM brievenbusevent WHERE gebruikersID = %s'

    @staticmethod
    def set_latest_setting(setting):
        sql = 'insert into Settingschange (`value`, time) values (%s, now());'
        params = [setting]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_latest_setting():
        sql = 'select value from Settingschange order by time DESC LIMIT 1'
        return Database.get_one_row(sql)

    @staticmethod
    def load_graph_data(weeknr):
        sql = 'select count(*) as `Aantal`, dayname(date) as `Day` from brievenbusevent where week(date, 5) = week(now(), 5) + %s and ActieID = 3 and deleted = 0 group by dayname(date) order by date DESC'
        params = [weeknr]
        return Database.get_rows(sql, params)

    @staticmethod
    def get_emails():
        sql = 'select email from gebruiker where email is not null'
        return Database.get_rows(sql)
