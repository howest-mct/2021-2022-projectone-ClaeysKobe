from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_sensor_gesch():
        sql = "SELECT * from historiek order by actiedatum DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensor_gesch_today():
        sql = "select * from historiek where cast(actiedatum as Date) = cast(now() as Date) order by actiedatum DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_latest_lid():
        sql = "select * from historiek where cast(actiedatum as Date) = cast(now() as Date) order by actiedatum DESC LIMIT 1"
        return Database.get_one_row(sql)

    @staticmethod
    def insert_magnet_value(status, beschrijving):
        sql = "INSERT INTO historiek(actiedatum, waarde, commentaar, DeviceID, ActieID) VALUES(now(), %s, %s, 12, 7)"
        params = [status, beschrijving]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_box_value(status, beschrijving):
        sql = "INSERT INTO historiek(actiedatum, waarde, commentaar, DeviceID, ActieID) VALUES(now(), %s, %s, 11, 6)"
        params = [status, beschrijving]
        return Database.execute_sql(sql, params)
