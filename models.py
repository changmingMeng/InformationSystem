from peewee import *

database = PostgresqlDatabase('testdb', **{'password': '123456', 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class CellInfo2G(BaseModel):
    bts = TextField(null=True)
    ci = TextField(null=True)
    lac = TextField(null=True)
    name = TextField(primary_key=True)

    class Meta:
        db_table = 'cell_info_2g'

class CellBusi2G(BaseModel):
    alldata = DecimalField(null=True)
    date = DateField()
    downdata = DecimalField(null=True)
    erl = DecimalField(null=True)
    name = ForeignKeyField(db_column='name', rel_model=CellInfo2G, to_field='name')
    updata = DecimalField(null=True)

    class Meta:
        db_table = 'cell_busi_2g'
        indexes = (
            (('name', 'date'), True),
        )
        primary_key = CompositeKey('date', 'name')

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

class CellInfo4G(BaseModel):
    base = TextField(db_column='base_id', null=True)
    base_name = TextField(null=True)
    cell = TextField(db_column='cell_id', null=True)
    name = TextField(primary_key=True)
    pci = TextField(null=True)
    tac = TextField(null=True)

    class Meta:
        db_table = 'cell_info_4g'

class CellBusi4G(BaseModel):
    alldata = DecimalField(null=True)
    date = DateField()
    downdata = DecimalField(null=True)
    erl = DecimalField()
    name = ForeignKeyField(db_column='name', rel_model=CellInfo4G, to_field='name')
    updata = DecimalField(null=True)

    class Meta:
        db_table = 'cell_busi_4g'
        indexes = (
            (('name', 'date'), True),
        )
        primary_key = CompositeKey('date', 'name')

def multi_insert(table, namelist):
    for name in namelist:
        database.execute_sql('INSERT INTO %s VALUE (%s)', (table, name))

def execute_sql(sql):
    return database.execute_sql(sql)