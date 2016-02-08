from myflaskapp import app, connection


# command to access db: psql trackfinity adminvjvhien


def createUserTable():
	connection.execute(    
		"""
	    CREATE TABLE users (
	        username VARCHAR PRIMARY KEY,
	        password VARCHAR NOT NULL
	    );
	    """
    )


def createUser(un, pw):
	rt_message = 0

	query_str = ("""SELECT * FROM users WHERE username='%s' """ % (un))

	if connection.execute(query_str).rowcount > 0:
		rt_message = 0
	else:
		query_str = ("""INSERT INTO users (username, password) VALUES ('%s', '%s'); """ % (un, pw))
		if connection.execute(query_str):
			rt_message = 1

	return rt_message

def getUser(un, pw):
	query_str = ("""SELECT * FROM users WHERE username='%s' AND password='%s'; """ % (un, pw))
	result = connection.execute(query_str)

	return result.rowcount