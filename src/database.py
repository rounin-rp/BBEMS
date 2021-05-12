import mysql.connector

#this function will connect to the database
def connectDatabase(hostname,username,psswd,databasename):
    mydb = mysql.connector.connect(
        host=hostname,
        user=username,
        password=psswd,
        database=databasename
        )
    return mydb


#this function will execute select query
def executeSelectQuery(myCursor,query):
    myCursor.execute(query)
    myResult = myCursor.fetchall()
    return myResult

#this function will execute insert query
def executeInsertQuery(mydb,myCursor,query):
    myCursor.execute(query)
    mydb.commit()