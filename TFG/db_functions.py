import sqlite3

conn = sqlite3.connect('./db/database.db', check_same_thread = False)
c = conn.cursor()

def create_table(name_table):
	c.execute('CREATE TABLE IF NOT EXISTS {}(Codigo_Donacion TEXT, Fecha DATE, UNIQUE(Codigo_Donacion, Fecha))'.format(name_table))

def create_table0(name_table):
	c.execute('CREATE TABLE IF NOT EXISTS {}(Codigo_Donacion TEXT, UNIQUE(Codigo_Donacion))'.format(name_table))

def add_donation_code(name_table, donation_code, dates):
	c.execute('INSERT OR IGNORE INTO {}(Codigo_Donacion, Fecha) VALUES ("{}", "{}")'.format(name_table, donation_code, dates))
	conn.commit()

def add_donation_code0(name_table, donation_code):
	c.execute('INSERT OR IGNORE INTO {}(Codigo_Donacion) VALUES ("{}")'.format(name_table, donation_code))
	conn.commit()

def column_exists(name_table, type_info):
	try: 
		c.execute('SELECT {} FROM {}'.format(type_info, name_table))
		return True
	except:
		return False

def create_columns(name_table, type_info):
	c.execute('ALTER TABLE {} ADD COLUMN \"{}\" TEXT'.format(name_table, type_info))
	conn.commit()

def add_data(name_table, donation_code, date, type_info, data_info):
	str = 'UPDATE {} SET {} = "{}" WHERE Codigo_Donacion = "{}" AND Fecha = "{}"'.format(name_table, type_info, data_info, donation_code, date)
	c.execute(str)
	conn.commit()

def add_data0(name_table, donation_code, type_info, data_info):
	str = 'UPDATE {} SET {} = "{}" WHERE Codigo_Donacion = "{}"'.format(name_table, type_info, data_info, donation_code)
	c.execute(str)
	conn.commit()	

##########################################################################################################

def view_all_tables():
	c.execute('SELECT name from sqlite_master where type= "table"')
	tables = c.fetchall()
	return tables

def view_all_columns(table, donation_code = None):
	if donation_code is None:
		cursor = conn.execute('SELECT * FROM {}'.format(table))
	else:
		cursor = conn.execute('SELECT * FROM {} WHERE Codigo_Donacion = "{}"'.format(table, donation_code))
	names = list(map(lambda x: x[0], cursor.description))
	return names

def view_all_data(table, donation_code = None):
	if donation_code is None:
		c.execute('SELECT * FROM {}'.format(table))
	else:
		c.execute('SELECT * FROM {} WHERE Codigo_Donacion = "{}"'.format(table, donation_code))
	data = c.fetchall()
	return data

def view_donation_code(table):
	c.execute('SELECT Codigo_Donacion FROM {}'.format(table))
	donation_code = c.fetchone()
	return donation_code[0]

def view_search(table, search, donation_code = None):
	try:
		if donation_code is None:
			c.execute('SELECT Codigo_Donacion, Fecha, {} FROM {}'.format(search, table))
		else:
			c.execute('SELECT Fecha, {} FROM {} WHERE Codigo_Donacion = "{}"'.format(search, table, donation_code))
		data = c.fetchall()
		return data
	except:
		return None

##########################################################################################################

def get_info(table, column, donation_code):
	try:
		c.execute('SELECT {} FROM {} WHERE Codigo_Donacion = "{}"'.format(column, table, donation_code))
		data = c.fetchone()
		return data[0]
	except:
		return 0
