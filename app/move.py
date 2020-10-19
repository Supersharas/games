
import json
from app.models import Game, Player, State, Offer, db
from auth import auth_auth
import sys
#from sqlalchemy import or_

from app import app, db # app only for error loging
from app.chessEngine import reffery, calculate_moves, legal

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


def move_maker(figure, move_number, game_id, promote, move):
	error = False
	authorized = auth_auth()
	if figure:
		if authorized:
			state = State.query.filter_by(game_id=game_id).order_by(State.move_number.desc()).first()
			app.logger.info('state: %s' % state)
			check = legal(state, figure, move)
			try:
				if check == 1:
					app.logger.info('check 1')
					legal_move = reffery(state, figure, move, promote)
					next_state = State(game_id=state.game_id, move_number=state.move_number+1, move=legal_move['next_move'], position=legal_move['new_position'], 
					white_timer=legal_move['time']['white'], black_timer=legal_move['time']['black'], time_limit=state.time_limit)
					State.insert(next_state)
					data = next_state.format()
					cash_put(state.game_id, state.move_number+1)
				if check == 'WKing':
					app.logger.info('check white')
					game = Game.query.filter_by(id=gameId).first()
					game.winner = game.player_one
					position = state.position
					position['WKing']['surrender'] = True;
					next_state = State(game_id=state.game_id, move_number=state.move_number+1, move='none', position=position, white_timer='0', black_timer=state.black_timer, time_limit=state.time_limit)
					data = next_state.format()
					State.insert(next_state)
				if check == 'BKing':
					app.logger.info('check black')
					game = Game.query.filter_by(id=gameId).first()
					game.winner = game.player_two
					position = state.position
					position['BKing']['surrender'] = True;
					next_state = State(game_id=state.game_id, move_number=state.move_number+1, move='none', position=position, white_timer=state.white_timer, black_timer='0', time_limit=state.time_limit)
					data = next_state.format()
					State.insert(next_state)
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
	if move_number:
		app.logger.info('move_number')
		if authorized:
			cashed = cash_get(game_id, move_number)
			if cashed:
				return json.dumps(None)
			#state = State.query.join(Game).filter(or_(Game.player_one==authorized, Game.player_two==authorized).order_by(State.move_number.desc()).first()
			state = State.query.filter_by(game_id=game_id).order_by(State.move_number.desc()).first()
			new_state = state.format()
			db.session.close()
			if move_number < new_state['move_number']:
				return json.dumps(new_state)
			else:
				return json.dumps(None)
	else:
		app.logger.info('no_move_number')
		state = State.query.filter_by(game_id=game_id).order_by(State.move_number.desc()).first()
		check = legal(state, None, None)
		if check == 'BKing':
			game = Game.query.filter_by(id=game_id).first()
			game.winner = game.player_two
			position = state.position
			position['BKing']['surrender'] = True;
			next_state = State(game_id=state.game_id, move_number=state.move_number+1, move='none', position=position, white_timer=state.white_timer, black_timer='0', time_limit=state.time_limit)
			data = next_state.format()
			State.insert(next_state)
		elif check == 'WKing':
			app.logger.info('check white')
			game = Game.query.filter_by(id=game_id).first()
			game.winner = game.player_one
			position = state.position
			position['WKing']['surrender'] = True;
			next_state = State(game_id=state.game_id, move_number=state.move_number+1, move='none', position=position, white_timer='0', black_timer=state.black_timer, time_limit=state.time_limit)
			data = next_state.format()
			State.insert(next_state)
		else:        
			data = state.format()
		db.session.close()
		return json.dumps(data)