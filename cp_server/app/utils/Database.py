from django.db import connection


class Database:
    def __init__(self,logger):
        self.logger = logger

    def select(self, sql, params=None):

        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            rawData = cursor.fetchall()
            data = []
            col_names = [desc[0] for desc in cursor.description]

            for row in rawData:
                d = {}
                for index, value in enumerate(row):
                    d[col_names[index]] = value

                data.append(d)

        except Exception as e:
            self.logger.error("Database.select() error sql=%s, params=%s, e=%s"%(str(sql), str(params), str(e)))
            data = []

        return data

    def insert(self, tb_name, d):

        sql = "insert into %s(%s) values(%s)" % (
            tb_name, ",".join(d.keys()), ",".join(map(lambda x: "'" + str(x) + "'", d.values())))

        return self.execute(sql)

    def execute(self, sql, params=None):

        ret = False
        try:
            cursor = connection.cursor()
            if params:
                e = cursor.execute(sql, params)
            else:
                e = cursor.execute(sql)
            # print(type(e), e)
            ret = True
        except Exception as e:
            self.logger.error("Database.execute() error sql=%s, params=%s, e=%s"%(str(sql), str(params), str(e)))

        return ret
