import db_create, db_delete

def db_reset():
    db_delete.db_delete()
    db_create.db_create()

if __name__ == "__main__":
    db_reset()
