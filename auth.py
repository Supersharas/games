
from flask import session
from app.models import Player
from app import app, db # app only for error loging

import secrets
import hashlib
import string

import sys

salt = b'\xb1\xc6\xd4\xe8[\xae\xdc\xb7\xb6\xb9h\x90\xda3J$`8\x04\x1e'

def Random(n):
  res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                                                  for i in range(n))
  return res


def auth_login(username, password):
	error = False
	wrong_user = False
	wrong_password, something, please_enter = None, None, None
	pa = password.encode()
	h = hashlib.sha256(pa + salt).hexdigest()
	if username and password:
		try:
			player = Player.query.filter_by(name=username).first()
			if player:
				if player.password != h:
					error = True
					wrong_password = 'Wrong password'
				else:
					random = Random(10)
					#session.clear()
					player.random = random
					db.session.commit()
					session['user'] = username
					session['info'] = random
					session['userId'] = player.id
			else:
				error = True
				wrong_user = "Sutch username does not exists on our records"
		except:
			app.logger.info(sys.exc_info())
			error = True
			something = 'Something went wrong. Please try again.'
			db.session.rollback()
		finally:
			db.session.close()
	else:
		error = True
		please_enter = 'Please provide user name and password!'
	if error:
		return {'success': False, 'wrong_user': wrong_user, 'wrong_password': wrong_password, 
		'please_enter': please_enter, 'something': something}
	else:
		return {'success': True}

def auth_register():
	print('registering')


def auth_authenticate():
	print('authenticating')