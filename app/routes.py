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

#app = Flask(__name__, static_folder='static' )
#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#app.debug = True

#setup_db(app)

# CASH ONLY FOR DEVELOPMENT
returned = []
games = {}

def cash_get(game, move_n):
  for key in games:
    if key == game:
      if games[key] == move_n:
        returned.append('yes')
        return True
  games[game] = move_n
  return False

def cash_put(user, move_n):
  games[user] = move_n

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
  error = False
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

@app.route('/chess/commence', methods=['POST'])
def commence():
  error = False
  content = json.loads(request.data)
  game_privacy = content.get('gamePrivacy', None)
  duration = content.get('duration', None)
  #return json.dumps({'privacy': game_privacy, 'duration': duration})
  auth = auth_auth()
  if auth['success']:
    app.logger.info(auth)
    player_id = auth['user_id']
  else:
    app.logger.info('player guest')
    player_id = auth_guest()
  try:
    app.logger.info('trying')
    if game_privacy == 'public':
      app.logger.info('we are geme privacy')
      offer = Offer.query.filter_by(public=True).filter_by(time_limit=duration).first()
      if offer:
        app.logger.info('we are offer')
        new_game = Game(player_one=offer.player_one, player_two = player_id, time_limit=duration)
        Game.insert(new_game)
        game = new_game.id
        offer.delete()
        current_state = State(game_id=new_game.id, move_number=1,move='white', position=calculate_moves(), time_limit=duration)
        State.insert(current_state)
        db.session.close()
        return json.dumps({'status': 'redirect', 'id': game})
    app.logger.info('we are here')
    offer = Offer(player_one = player_id, time_limit=duration)
    Offer.insert(offer)
    offer_id = offer.id
    db.session.close()
    return json.dumps({'status': 'waiting', 'offerId': offer_id})
  except:
    app.logger.info(sys.exc_info())
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    return json.dumps({'status': 'error'})

@app.route('/chess/move', methods=['GET', 'POST'])
def move():
  error = False
  if request.method == 'POST':
    content = json.loads(request.data)
    figure = content.get('figure', None)
    promote = content.get('promote', None)
    move_number = content.get('moveNumber', None)
    gameId = content.get('gameId', None)
    app.logger.info('gameId: %s' % gameId)
    if figure:
      if session['userId']:
        state = State.query.filter_by(game_id=gameId).order_by(State.move_number.desc()).first()
        app.logger.info('state: %s' % state)
        check = legal(state, figure, content['move'])
        if check == 1:
          try:
            legal_move = reffery(state, figure, content['move'], promote)
            next_state = State(game_id=state.game_id, move_number=state.move_number+1, move=legal_move['next_move'], position=legal_move['new_position'], 
            white_timer=legal_move['time']['white'], black_timer=legal_move['time']['black'])
            State.insert(next_state)
            data = next_state.format()
            cash_put(state.game_id, state.move_number+1)
          except:
            error = True
            db.session.rollback()
            app.logger.info(sys.exc_info())
            app.logger.info(sys.argv[1])
          finally:
            db.session.close()
          if error:
            return json.dumps({'error': True})
          return json.dumps(data)
          #return json.dumps({'promotion': data})
        else:
          return json.dumps({'error': check})
    if move_number:
      if session['userId']:
        cashed = cash_get(gameId, move_number)
        if cashed:
          return json.dumps(None)
        state = State.query.join(Game).filter(or_(Game.player_one==session['userId'], Game.player_two==session['userId'])).order_by(State.move_number.desc()).first()
        new_state = state.format()
        db.session.close()
        if move_number < new_state['move_number']:
          return json.dumps(new_state)
        else:
          return json.dumps(None)
  else:
    return json.dumps({'kas': 'per huiniene'})
  
@app.route('/chess/black/<int:game>')
def black(game):
  state = State.query.filter_by(game_id=game).order_by(State.move_number.desc()).first()
  data = state.format()
  player = state.games.player
  oponent = state.games.oponent
  # ONLY FOR TESTING
  session['userId'] = oponent.id
  db.session.close()
  return render_template('black.html', data=json.dumps(data), player=oponent, oponent=player, game_id=game)

@app.route('/chess/white/<int:game>')
def white(game):
  state = State.query.filter_by(game_id=game).order_by(State.move_number.desc()).first()
  data = state.format()
  player = state.games.player
  # ONLY FOR TESTING
  session['userId'] = player.id
  oponent = state.games.oponent
  move_number = state.id
  #time_test = time_master(state.date, state.white_timer, state.black_timer, move)
  db.session.close()
  return render_template('white.html', data=json.dumps(data), player=player, oponent=oponent, game_id=game, move_number=move_number)#, time=time_test)

@app.route('/chess')
def chess():
  user = 0
  my_games = ''
  if 'user' in session:
    app.logger.info('checking')
    auth = auth_auth()
    app.logger.info('info')
    app.logger.info(session['info'])
    if auth:
      player = Player.query.filter_by(id=auth['user_id']).first()
      games = Offer.query.filter(Offer.player_one!=auth['user_id']).all()
      my_games = Offer.query.filter_by(player_one=auth['user_id']).all()
      user = auth['user']
    else:
      app.logger.info(player.random, session['info'])
      return 'Stop!!! No trespasing'
  else:
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
    print(sys.exc_info())
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

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    #session.pop('userId', None)
    session.clear()
    return redirect(url_for('chess'))
#if __name__ == '__main__':
#  app.run(host='0.0.0.0', port=8080)
  #socketio.run(app, host='0.0.0.0', port=8080)