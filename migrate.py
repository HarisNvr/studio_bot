from sql_orm import Base, engine

Base.metadata.create_all(engine)
