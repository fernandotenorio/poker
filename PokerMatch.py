from Deck import *
from random import choice

class PokerPlayer(object):
	def __init__(self, name):
		self.name=name
		self.is_out = False
		self.cards = []


	def act(self, options):		
		#return choice(options)
		return choice(options)

	def __str__(self):
		return self.name

	
class PokerMatch(object):
	def __init__(self, nplayers):
		self.nplayers = nplayers
		self.button_idx = 0
		self.sb_idx = 1
		self.bb_idx = 2		
		self.players = [PokerPlayer('player' + str(i)) for i in range(nplayers)]
		self.smallBlind = 1
		self.bigBlind = 2 * self.smallBlind
		self.pot = 0
		self.deck = PokerDeck()
		self.communityCards = []

		for _ in range(2):
			for p in self.players:
				p.cards.append(self.deck.pick())


	def rotate(self):
		self.button_idx = (self.button_idx + 1) % self.nplayers
		self.sb_idx = (self.sb_idx + 1) % self.nplayers
		self.bb_idx = (self.bb_idx + 1) % self.nplayers


	# def get_player_to_left(self, player):
	# 	idx = self.players.index(player)
	# 	next_idx = (idx + 1) % self.nplayers
	# 	return self.players[next_idx]

	# next player
	def get_player_to_left(self, player):
		tmp = player
		while True:
			idx = self.players.index(player)
			next_idx = (idx + 1) % self.nplayers
			player = self.players[next_idx]

			if not player.is_out:
				assert player != tmp, 'get_player_to_left error'
				return next_idx, player


	# player before
	def get_player_to_right(self, player):
		tmp = player
		while True:
			idx = self.players.index(player)
			next_idx = idx - 1 if idx > 0 else self.nplayers - 1
			player = self.players[next_idx]

			if not player.is_out:
				assert player != tmp, 'get_player_to_right error'
				return next_idx, player



	def preflop(self):
		done = False				
		_, currentPlayer = self.get_player_to_left(self.players[self.button_idx])		
		current_bet = self.bigBlind
		folded = 0  
		contributed = []

		for i in range(self.nplayers):
			if i == self.sb_idx:
				contributed.append(self.smallBlind)
			elif i == self.bb_idx:
				contributed.append(self.bigBlind)
			else:
				contributed.append(0)


		# idx of player that can close the round
		end_round_idx = self.bb_idx

		while not done:
			p_idx = self.players.index(currentPlayer)
			
			if contributed[p_idx] == current_bet:				
				act = currentPlayer.act(['check', 'raise'])

				if act == 'raise':					
					amount_raise = 1 * self.bigBlind
					raise_to = current_bet + amount_raise
					current_bet = raise_to
					contributed[p_idx]+= amount_raise					
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					print('{} raises to {}'.format(currentPlayer.name, raise_to))
				elif act =='check':
					print('{} Checks'.format(currentPlayer.name))
			else:
				amount_call = current_bet - contributed[p_idx]
				act = currentPlayer.act(['call', 'raise', 'fold'])

				if act == 'call':
					contributed[p_idx]+= amount_call
					print('{} Calls {}'.format(currentPlayer.name, amount_call))
				elif act == 'raise':					
					amount_raise = 1 * self.bigBlind
					raise_to = current_bet + amount_raise
					current_bet = raise_to
					contributed[p_idx]+= amount_call + amount_raise					
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					print('{} raises to {}'.format(currentPlayer.name, raise_to))
				elif act == 'fold':
					currentPlayer.is_out = True
					folded+= 1
					print('{} folds'.format(currentPlayer.name))


			if folded == self.nplayers - 1:
				return [p for p in self.players if not p.is_out], contributed
						
			if p_idx == end_round_idx:
				done = True				
			else:
				_, currentPlayer = self.get_player_to_left(currentPlayer)

		return [p for p in self.players if not p.is_out], contributed



	def flop(self, cc):
		done = False				
		_, currentPlayer = self.get_player_to_left(self.players[self.bb_idx])
		current_bet = None
		folded = 0  
		contributed = [0] * self.nplayers

		# idx of player that can close the round
		end_round_idx, _ = self.get_player_to_right(currentPlayer)

		# community cards
		for i in range(cc):
			self.communityCards.append(self.deck.pick())


		while not done:
			p_idx = self.players.index(currentPlayer)
			
			if current_bet is None:
				act = currentPlayer.act(['bet', 'check'])

				if act == 'bet':										
					current_bet = self.bigBlind
					contributed[p_idx]+= current_bet
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					print('{} bets {}'.format(currentPlayer.name, current_bet))
				elif act =='check':
					print('{} Checks'.format(currentPlayer.name))
			else:
				amount_call = current_bet - contributed[p_idx]
				act = currentPlayer.act(['call', 'raise', 'fold'])

				if act == 'call':
					contributed[p_idx]+= amount_call
					print('{} Calls {}'.format(currentPlayer.name, amount_call))
				elif act == 'raise':					
					amount_raise = 1 * self.bigBlind
					raise_to = current_bet + amount_raise
					current_bet = raise_to
					contributed[p_idx]+= amount_call + amount_raise					
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					print('{} raises to {}'.format(currentPlayer.name, raise_to))
				elif act == 'fold':
					currentPlayer.is_out = True
					folded+= 1
					print('{} folds'.format(currentPlayer.name))


			if folded == self.nplayers - 1:
				return [p for p in self.players if not p.is_out], contributed
						
			if p_idx == end_round_idx:
				done = True				
			else:
				_, currentPlayer = self.get_player_to_left(currentPlayer)


		return [p for p in self.players if not p.is_out], contributed




if __name__ == '__main__':
	
	# for p in match.players:
	# 	print(p.name)
	# 	for c in p.cards:
	# 		print(c)
	# 	print('==='*5)

	for _ in range(1):
		print('Preflop round')
		match = PokerMatch(3)
		players, x = match.preflop()
		assert len(players) >= 1, 'Error in number of players'
		print([str(p) for p in players], x)

		if len(players) > 1:
			print('Flop round')
			players, x = match.flop(3)
			assert len(players) >= 1, 'Error in number of players'
			print([str(p) for p in players], x)
			print([str(c) for c in match.communityCards])

		if len(players) > 1:
			print('Turn round')
			players, x = match.flop(1)
			assert len(players) >= 1, 'Error in number of players'
			print([str(p) for p in players], x)
			print([str(c) for c in match.communityCards])

		if len(players) > 1:
			print('River round')
			players, x = match.flop(1)
			assert len(players) >= 1, 'Error in number of players'
			print([str(p) for p in players], x)
			print([str(c) for c in match.communityCards])

		print('========'*10)
	





# 	     D

#  P			SB

#    UTG   BB