
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

def auth_register(username, password, password2):
  error = False
  wrong_password, something, please_enter, user_exists = None, None, None, None
  if username and password and password2:
    if password == password2:
      check_player = Player.query.filter_by(name=username).first()
      if not check_player:
        try:
          pa = password.encode()
          h = hashlib.sha256(pa + salt).hexdigest()
          random = Random(10)
          player = Player(name=username, password=h, random=random) 
          Player.insert(player)
          user_id = player.id
        except:
          app.logger.info(sys.exc_info())
          error = True
          something = 'Something went wrong. Please try again.'
          db.session.rollback()
        finally:
          db.session.close()
      else:
        error = True
        user_exists = 'Username unawailable. Such user allready exists'
    else:
      error = True
      wrong_password = 'Passwords does not match'
  else:
    error = True
    please_enter = 'Please provide user name and password!'
  if error:
    return {'success': False, 'passwordMsgRe': wrong_password, 'userExists': user_exists,
		'enterMsgRe': please_enter, 'something': something}
  else:
    session['user'] = username
    session['info'] = random
    session['userId'] = user_id
    return {'success': True}


def auth_auth(loc=False):
  error = False
  user = session.get('user', None)
  user_id = session.get('userId', None)
  info = session.get('info', None)
  app.logger.info(user)
  app.logger.info(user_id)
  app.logger.info(info)
  if user_id:
    try:
      player = Player.query.filter_by(id=user_id).first()
      random = player.random
      if loc:
        player.location = loc
        Player.update(Player)
    except:
      app.logger.info(sys.exc_info())
      error = True
      db.session.rollback()
    finally:
      db.session.close()
  else:
    return {'success': False}
  if error or random != info:
    return {'success': False}
  else:
    return {'success': True, 'user': user, 'user_id': user_id}

def auth_guest():
  error = False
  random = Random(10)
  try:
    player = Player(random=random)
    Player.insert(player)
    player.name = 'Guest ' +  str(player.id)
    Player.update(player)
    player_id = player.id
    session['userId'] = player.id
    session['info'] = player.random
    session['user'] = player.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    False
  else:
    return player_id
  