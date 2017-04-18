from peewee import *

database = PostgresqlDatabase('testdb', **{'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Cell(BaseModel):
    base_station = TextField(null=True)
    cell = TextField(null=True)
    id = TextField()
    nettype = UnknownField()  # USER-DEFINED
    sector = TextField(null=True)

    class Meta:
        db_table = 'cell'
        indexes = (
            (('id', 'nettype'), True),
        )
        primary_key = CompositeKey('id', 'nettype')

class CellInfo3G(BaseModel):
    ci = TextField(null=True)
    fac = TextField(null=True)
    lac = TextField(null=True)
    name = TextField(primary_key=True)
    nodeb = TextField(null=True)
    rnc = TextField(null=True)

    class Meta:
        db_table = 'cell_info_3g'

class CellBusi3G(BaseModel):
    alldata = DecimalField(null=True)
    date = DateField()
    downdata = DecimalField(null=True)
    erl = DecimalField(null=True)
    name = ForeignKeyField(db_column='name', rel_model=CellInfo3G, to_field='name')
    updata = DecimalField(null=True)

    class Meta:
        db_table = 'cell_busi_3g'
        indexes = (
            (('name', 'date'), True),
        )
        primary_key = CompositeKey('date', 'name')

class CellData(BaseModel):
    alldata = DecimalField()
    date = DateField()
    downdata = DecimalField()
    erl = DecimalField(null=True)
    id = TextField(index=True)
    nettype = UnknownField()  # USER-DEFINED
    time = TimeField()
    updata = DecimalField()

    class Meta:
        db_table = 'cell_data'
        indexes = (
            (('date', 'time', 'nettype', 'id'), True),
        )
        primary_key = CompositeKey('date', 'id', 'nettype', 'time')

class CellInfo2G(BaseModel):
    btsname = TextField(null=True)
    ci = TextField(null=True)
    lac = TextField(null=True)
    name = TextField(primary_key=True)

    class Meta:
        db_table = 'cell_info_2G'

def multi_insert(table, namelist):
    for name in namelist:
        database.execute_sql('INSERT INTO %s VALUE (%s)', (table, name))

def execute_sql(sql):
    return database.execute_sql(sql)