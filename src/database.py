import mysql.connector

#this function will connect to the database
def connectDatabase(hostname,username,psswd,databasename):
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        password=psswd,
        database=databasename,
        auth_plugin='mysql_native_password'
        )
    return mydb


#this function will execute select query
def executeSelectQuery(myCursor,query):
    myCursor.execute(query)
    myResult = myCursor.fetchall()
    if len(myResult):
        return myResult
    else:
        return False

#this function will execute insert query
def executeInsertQuery(mydb,myCursor,query):
    myCursor.execute(query)
    mydb.commit()