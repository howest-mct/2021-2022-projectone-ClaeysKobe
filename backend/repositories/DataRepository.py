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
        sql = "SELECT * from historiek"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensor_gesch_today():
        sql = "select * from historiek where cast(actiedatum as Date) = cast(now() as Date)"
        return Database.get_rows(sql)
