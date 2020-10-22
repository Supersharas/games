from app import app

from flask import url_for, jsonify, request, session, redirect
from flask import render_template
from sqlalchemy import or_
import sys
import json
from markupsafe import escape 

from app.chessEngine import reffery, calculate_moves, legal
from auth import auth_login, auth_register, auth_auth, auth_guest
from app.models import Game, Player, State, Offer, db
from app.move import move_maker, move_commence

@app.route('/cash')
def check_cash():
	return render_template('cash.html',ret=returned, games=games)

@app.route('/')
def hello_world():
		return redirect(url_for('chess'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form.get('userName')
		password = request.form.get('password')
		authenticating = auth_login(username, password)
		if not authenticating['success']:
			return render_template('login.html', userMsg=authenticating['wrong_user'], 
				passwordMsg=authenticating['wrong_password'], enterMsg=authenticating['please_enter'], 
				something=authenticating['something'])
		else:
			return redirect(url_for('chess'))

	return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
	username = request.form.get('userName')
	password2 = request.form.get('repeatPassword')
	password = request.form.get('password')
	registering = auth_register(username, password, password2)
	if not registering['success']:
		return render_template('login.html', passwordMsgRe=registering['wrong_password'], enterMsgRe=registering['please_enter'], something=registering['something'], userExists=registering['user_exists'])
	else:
		return redirect(url_for('chess'))



@app.route('/startGame/<int:offer>')
def start_game(offer):
	try:
		if 'userId' in session:
			player_id = session['userId']
		else:
			player = Player()
			Player.insert(player)
			player_id = player.id
			session['userId'] = player.id
		offer = Offer.query.filter_by(id=offer).first()
		new_game = Game(player_one=offer.player_one, player_two = player_id)
		Game.insert(new_game)
		game = new_game.id
		offer.delete()
		current_state = State(game_id=new_game.id, move_number=1,move='white',position=calculate_moves())
		State.insert(current_state)
	except:
		error = True
		db.session.rollback()
		print(sys.exc_info())
	finally:
		db.session.close()
	if error:
		return 'start game error'
	else:
		return redirect(url_for('white', game = game))

@app.route('/chess/rematch', methods=['GET','POST'])
def rematch():
	error = False
	if request.method == 'POST':
		content = json.loads(request.data)
		game_id = content.get('gameId', None)
		oponent_id = content.get('oponent', None)
		player_id = content.get('player', None)
		play_again = content.get('playAgain', None)
		#create offer
		try:
			if play_again:
				player = Player.query.filter_by(id=player_id).first()
				player.location = 'offered' + str(game_id)
				Player.update(player)
			oponent = Player.query.filter_by(id=oponent_id).first()
			oponent_loc = oponent.location
		except:
			error = True
			db.session.rollback()
		db.session.close()
		if error or (oponent_loc != str(game_id) and oponent_loc != 'offered' + str(game_id)):
			return json.dumps({'left': True})
		elif oponent_loc == 'offered' + str(game_id):
			return json.dumps({'offered': True})
		return json.dumps({'game_id': game_id, 'oponent': oponent_loc})
	if request.method == 'GET':
		#redirect to game
		return redirect(url_for('chess'))

@app.route('/chess/commence', methods=['POST'])
def commence():
	content = json.loads(request.data)
	game_privacy = content.get('gamePrivacy', None)
	duration = content.get('duration', None)
	return move_commence(game_privacy, duration)

@app.route('/chess/move', methods=['GET', 'POST'])
def move():
	if request.method == 'POST':
		content = json.loads(request.data)
		figure = content.get('figure', None)
		promote = content.get('promote', None)
		move_number = content.get('moveNumber', None)
		game_id = content.get('gameId', None)
		move = content.get('move', None)
		return move_maker(figure, move_number, game_id, promote, move)
	else:
		return json.dumps({'kas': 'per huiniene'})
	
@app.route('/chess/black/<int:game>')
def black(game):
  user = session['user']
  state = State.query.filter_by(game_id=game).order_by(State.move_number.desc()).first()
  data = state.format()
  player = state.games.player
  oponent = state.games.oponent
  # ONLY FOR TESTING
  db.session.close()
  return render_template('black.html', data=json.dumps(data), player=player, oponent=oponent, game_id=game, user=user)

@app.route('/chess/white/<int:game>')
def white(game):
  user = session['user']
  state = State.query.filter_by(game_id=game).order_by(State.move_number.desc()).first()
  data = state.format()
  player = state.games.player
  # ONLY FOR TESTING
  oponent = state.games.oponent
  move_number = state.id
  #time_test = time_master(state.date, state.white_timer, state.black_timer, move)
  db.session.close()
  #app.logger.info(player)
  return render_template('white.html', data=json.dumps(data), player=oponent, oponent=player, game_id=game, move_number=move_number, user=user)#, time=time_test)

@app.route('/chess')
def chess():
  user = 0
  my_games = ''
  auth = auth_auth('chess')
  app.logger.info(auth)
  if auth['success']:
    #player = Player.query.filter_by(id=auth['user_id']).first()
    games = Offer.query.filter(Offer.player_one!=auth['user_id']).all()
    my_games = Offer.query.filter_by(player_one=auth['user_id']).all()
    user = auth['user']
  games = Offer.query.all()
  return render_template('chess.html', offers=games, my_games=my_games, user=user)

@app.route('/offer')
def offer():
	error = False
	try:
		player = Player()
		Player.insert(player)
		offer = Offer(player_one = player.id)
		Offer.insert(offer)
		session['userId'] = player.id
	except:
		error = True
		db.session.rollback()
	finally:
		db.session.close()
	if error:
		return 'offer error'
	else:
		return redirect(url_for('chess'))

@app.route('/chess/lobby')
def lobby():
	nice_game = 'none'
	nice_offers = []
	offers = Offer.query.all()
	if 'userId' in session:
		my_game = Game.query.filter_by(player_one=session['userId']).first()
		if my_game:
			nice_game = my_game.format()
	for offer in offers:
		nice_offers.append(offer.format())
	db.session.close()
	return jsonify({'offers': nice_offers, 'game' : nice_game})

@app.route('/chess/lobby', methods = ['POST'])
def lobby_post():
  game_id = None
  content = json.loads(request.data)
  offer_id = content.get('offerId', None)
  try:
    game = Game.query.filter_by(offer_id=offer_id).first()
    game_id = game.id
    app.logger.info(game)
  except:
    db.session.rollback()
    app.logger.info(sys.exc_info())
  finally:
    db.session.close()
  if game_id:
    #WE NEED A GAME HERE
    return jsonify({'url': url_for('black', game = game_id)})
  else:
    return jsonify({'status': 'not yet'})


@app.route('/logout')
def logout():
		# remove the username from the session if it's there
		#session.pop('userId', None)
		session.clear()
		return redirect(url_for('chess'))
#if __name__ == '__main__':
#  app.run(host='0.0.0.0', port=8080)
	#socketio.run(app, host='0.0.0.0', port=8080)