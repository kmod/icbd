from sqlalchemy import Table
from sqlalchemy import schema, types, select, and_
from sqlalchemy.orm import scoped_session
from sqlalchemy.engine import create_engine

metadata = schema.MetaData()

t1 = Table("t1", metadata,
        schema.Column("id", types.Integer),
        schema.Column("v", types.String),
)

t1.c.id # 5 Column 'id' (int)
t1.c.v # 5 Column 'v' (str)

Session = scoped_session(1) # 0 ScopedSession

r = Session.connection().execute(select([t1.c.id], and_())) # 0 ResultProxy (t1)
r1 = r.fetchone() # 0 RowProxy (t1)
r1.id # 3 int
r1.v # e 0
r2 = r.fetchall() # 0 [RowProxy (t1)]
r3 = r.scalar() # 0 int

r = Session.connection().execute(t1.select().where(t1.c.id == 1))
r1 = r.fetchone()
r1.id # 3 int
r1.v # 3 str
r2 = r.fetchall()
r3 = r.scalar() # 0 int

r = Session.connection().execute([t1.c.v], t1.c.id == 1)
r1 = r.fetchone()
r1.id # e 0
r1.v # 3 str
r2 = r.fetchall()
r3 = r.scalar() # 0 str

r = Session.connection().execute((t1.c.v,), t1.c.id == 1)
r1 = r.fetchone()
r1.id # e 0
r1.v # 3 str
r2 = r.fetchall()
r3 = r.scalar() # 0 str

r = Session.connection().execute(t1.c.id, t1.c.id == 1)
r1 = r.fetchone()
r1.id # 3 int
r1.v # e 0
r2 = r.fetchall()
r3 = r.scalar() # 0 int

e = create_engine('')
r = e.execute(select((t1.c.id,), True))
r1 = r.fetchone()
r1.id # 3 int
r1.v # e 0
r2 = r.fetchall()
r3 = r.scalar() # 0 int

for x in r: # 4 RowProxy (t1) # 9 ResultProxy (t1)
    x.id # 6 int
    x.v # e 4

SessionProxy
