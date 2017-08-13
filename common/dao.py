import pymysql

class Dao(object):
    cursor = None
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': '',
        'charset':'utf8mb4',
        'db':'transfermarkt',
        'autocommit': True,
        'cursorclass':pymysql.cursors.DictCursor
    }

    @staticmethod
    def init():
        conn = pymysql.connect(**Dao.config)
        Dao.cursor = conn.cursor()

    @staticmethod
    def createEternalTable():
        sql  = 'create table if not exists eternal_table ('
        sql += 'id varchar(5) not null,'
        sql += 'league varchar(4) not null,'
        sql += 'level tinyint,'
        sql += 'years smallint,'
        sql += 'first smallint,'
        sql += 'appearance smallint,'
        sql += 'win smallint,'
        sql += 'draw smallint,'
        sql += 'loss smallint,'
        sql += 'goal smallint,'
        sql += 'point smallint,'
        sql += 'primary key (id, league)'
        sql += ')'
        Dao.cursor.execute(sql)

    @staticmethod
    def createClubTable():
        sql  = 'create table if not exists club ('
        sql += 'id varchar(5) not null,'
        sql += 'name varchar(40),'
        sql += 'nation smallint,'
        sql += 'founded varchar(4),'
        sql += 'ground varchar(50),'
        sql += 'capacity smallint,'
        sql += 'primary key (id)'
        sql += ')'
        Dao.cursor.execute(sql)

    @staticmethod
    def createPlayerTable():
        sql  = 'create table if not exists player ('
        sql += 'id varchar(10) not null,'
        sql += 'full_name varchar(30),'
        sql += 'name varchar(20),'
        sql += 'cname varchar(15),'
        sql += 'birthday varchar(8),'
        sql += 'nationality int,'
        sql += 'position tinyint,'
        sql += 'height tinyint,'
        sql += 'retirement tinyint,'
        sql += 'modify_date datetime,'
        sql += 'primary key (id)'
        sql += ')'
        Dao.cursor.execute(sql)

    @staticmethod
    def createCareerTable():
        sql  = 'create table if not exists career ('
        sql += 'id varchar(10) not null,'
        sql += 'season varchar(5),'
        sql += 'club varchar(5),'
        sql += 'appearance tinyint,'
        sql += 'assist tinyint,'
        sql += 'yellow tinyint,'
        sql += 'red tinyint,'
        sql += 'minute smallint,'
        sql += 'primary key (id, season, club)'
        sql += ')'
        Dao.cursor.execute(sql)

    def getClubCount(id):
        Dao.cursor.execute('select id from club where id = %s', id)
        return Dao.cursor.rowcount

    def getAllClubId():
        Dao.cursor.execute('select distinct id from club')
        return Dao.cursor.fetchall()

    def getEternalTableCount(id, league):
        Dao.cursor.execute('select id from eternal_table where id = %s and league = %s', (id, league))
        return Dao.cursor.rowcount

    def getPlayerCount(id):
        Dao.cursor.execute('select id from player where id = %s', (id))
        return Dao.cursor.rowcount

    def getCareerCount(id, season, club):
        Dao.cursor.execute('select id from career where id = %s and season = %s and club = %s', (id, season, club))
        return Dao.cursor.rowcount

    def getNotCompleteClub():
        Dao.cursor.execute('select id from club where founded is null or ground is null or capacity is null')
        return Dao.cursor.fetchall()

    def insertClub(param):
        sql = 'insert into club (id, name, nation) values(%s, %s, %s)'
        Dao.cursor.execute(sql, param)

    def insertEternalTable(param):
        sql = 'insert into eternal_table values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        Dao.cursor.execute(sql, param)

    def insertPlayer(param):
        sql = 'insert into player values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        Dao.cursor.execute(sql, param)

    def insertCareer(param):
        sql = 'insert into career values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        Dao.cursor.execute(sql, param)

    def updatePlayer(param):
        sql = 'update player set full_name = %s, name = %s, nationality = %s, position = %s, height = %s, modify_date = %s where id = %s'
        Dao.cursor.execute(sql, param)

    def updateCareer(param):
        sql = 'update career set appearance = %s, goal = %s, assist = %s, yellow = %s, red = %s, minute = %s where id = %s and season = %s and club = %s'
        Dao.cursor.execute(sql, param)

    def updateEternalTable(param):
        sql = 'update eternal_table set league = %s, level = %s, years = %s, first = %s, appearance = %s, win = %s, draw = %s, loss = %s, goal = %s, point = %s where id = %s'
        Dao.cursor.execute(sql, param)

    def updateClubExtraData(param):
        sql = 'update club set founded = %s, ground = %s, capacity = %s where id = %s'
        Dao.cursor.execute(sql, param)