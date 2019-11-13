from Deck import *
from random import choice
import itertools

class PokerPlayer(object):
	def __init__(self, name):
		self.name=name
		self.is_out = False
		self.cards = []

	def act(self, options):		
		pass		

	def __str__(self):
		return self.name


class AIPlayer(PokerPlayer):
	def __init__(self, name):
		super().__init__(name)

	def act(self, options):
		#return choice([o for o in options if o != 'fold'])
		return choice(options)


class HumanPlayer(PokerPlayer):
	def __init__(self, name):
		super().__init__(name)

	def act(self, options):
		print('Your cards:')
		print([str(c) for c in self.cards])

		print('Choose an action:')
		print(options)

		while True:
			opt = str(input()).lower()
			if opt in options:
				return opt
			else:
				print('Invalid action, try again:')
				print(options)

	
class PokerMatch(object):
	def __init__(self, players):
		self.nplayers = len(players)
		self.button_idx = 0
		self.sb_idx = 1
		self.bb_idx = 2		
		self.players = players#[PokerPlayer('player' + str(i)) for i in range(nplayers)]
		self.smallBlind = 1
		self.bigBlind = 2 * self.smallBlind
		self.pot = 0
		self.deck = PokerDeck()
		self.communityCards = []
		self.history = {'preflop': [], 'flop': [], 'turn': [], 'river': [], 'community_cards': {'flop': [], 'turn': [], 'river': []}}
		PokerMatch.MAX_RAISES = 4


	def rotate(self):
		self.button_idx = (self.button_idx + 1) % self.nplayers
		self.sb_idx = (self.sb_idx + 1) % self.nplayers
		self.bb_idx = (self.bb_idx + 1) % self.nplayers

		# reset
		self.pot = 0
		self.deck = PokerDeck()
		self.communityCards = []
		self.history = {'preflop': [], 'flop': [], 'turn': [], 'river': [], 'community_cards': {'flop': [], 'turn': [], 'river': []}}

		for p in self.players:
			p.is_out = False
			p.cards = []



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
		_, currentPlayer = self.get_player_to_left(self.players[self.bb_idx])		
		current_bet = self.bigBlind
		folded = 0  
		contributed = []

		# player cards
		for _ in range(2):
			for p in self.players:
				p.cards.append(self.deck.pick())

		# blinds
		for i in range(self.nplayers):
			if i == self.sb_idx:
				contributed.append(self.smallBlind)
			elif i == self.bb_idx:
				contributed.append(self.bigBlind)
			else:
				contributed.append(0)


		# idx of player that can close the round
		end_round_idx = self.bb_idx
		n_raises = 0

		while not done:
			p_idx = self.players.index(currentPlayer)			
			
			if contributed[p_idx] == current_bet:				
				act = currentPlayer.act(['check', 'raise'] if n_raises < PokerMatch.MAX_RAISES else ['check'])

				if act == 'raise':
					n_raises+= 1
					amount_raise = 1 * self.bigBlind
					raise_to = current_bet + amount_raise
					current_bet = raise_to
					contributed[p_idx]+= amount_raise					
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					str_log = '{} raises to {}'.format(currentPlayer.name, raise_to)
					print(str_log)
					print('Pot {}'.format(sum(contributed)))
					self.history['preflop'].append(str_log)					
				elif act =='check':
					str_log = '{} Checks'.format(currentPlayer.name)
					print(str_log)
					self.history['preflop'].append(str_log)					
			else:
				amount_call = current_bet - contributed[p_idx]
				act = currentPlayer.act(['call', 'raise', 'fold'] if n_raises < PokerMatch.MAX_RAISES else ['call', 'fold'])

				if act == 'call':
					contributed[p_idx]+= amount_call
					str_log = '{} Calls {}'.format(currentPlayer.name, amount_call)
					print(str_log)
					print('Pot {}'.format(sum(contributed)))
					self.history['preflop'].append(str_log)					
				elif act == 'raise':
					n_raises+= 1					
					amount_raise = 1 * self.bigBlind
					raise_to = current_bet + amount_raise
					current_bet = raise_to
					contributed[p_idx]+= amount_call + amount_raise					
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					str_log = '{} raises to {}'.format(currentPlayer.name, raise_to)					
					print(str_log)
					print('Pot {}'.format(sum(contributed)))
					self.history['preflop'].append(str_log)					
				elif act == 'fold':
					currentPlayer.is_out = True
					folded+= 1
					str_log = '{} folds'.format(currentPlayer.name)
					print(str_log)
					self.history['preflop'].append(str_log)					


			if folded == self.nplayers - 1:
				# exiting round, updating pot size
				self.pot+= sum(contributed)
				self.history['preflop'].append(self.pot)
				return [p for p in self.players if not p.is_out], contributed
						
			if p_idx == end_round_idx:
				done = True				
			else:
				_, currentPlayer = self.get_player_to_left(currentPlayer)

		# exiting round, updating pot size
		self.pot+= sum(contributed)
		self.history['preflop'].append(self.pot)
		return [p for p in self.players if not p.is_out], contributed



	def flop(self, cc, round_name):
		done = False				
		_, currentPlayer = self.get_player_to_left(self.players[self.button_idx])
		current_bet = None
		folded = 0  
		contributed = [0] * self.nplayers

		# idx of player that can close the round
		end_round_idx, _ = self.get_player_to_right(currentPlayer)
		n_raises = 0

		# community cards
		for i in range(cc):
			card = self.deck.pick()
			self.communityCards.append(card)
			self.history['community_cards'][round_name].append(str(card))

		print('{}: Community cards:'.format(round_name))
		print([str(c) for c in self.communityCards])

		while not done:
			p_idx = self.players.index(currentPlayer)			
			
			if current_bet is None:
				act = currentPlayer.act(['bet', 'check'])

				if act == 'bet':										
					current_bet = self.bigBlind
					contributed[p_idx]+= current_bet
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					str_log = '{} bets {}'.format(currentPlayer.name, current_bet)
					print(str_log)
					self.history[round_name].append(str_log)					
				elif act =='check':
					str_log = '{} Checks'.format(currentPlayer.name)
					print(str_log)
					self.history[round_name].append(str_log)					
			else:
				amount_call = current_bet - contributed[p_idx]
				act = currentPlayer.act(['call', 'raise', 'fold'] if n_raises < PokerMatch.MAX_RAISES else ['call', 'fold'])

				if act == 'call':
					contributed[p_idx]+= amount_call
					str_log = '{} Calls {}'.format(currentPlayer.name, amount_call)
					print(str_log)
					self.history[round_name].append(str_log)					
				elif act == 'raise':
					n_raises+= 1					
					amount_raise = 1 * self.bigBlind
					raise_to = current_bet + amount_raise
					current_bet = raise_to
					contributed[p_idx]+= amount_call + amount_raise					
					end_round_idx, _ = self.get_player_to_right(currentPlayer)
					str_log = '{} raises to {}'.format(currentPlayer.name, raise_to)
					print(str_log)
					self.history[round_name].append(str_log)					
				elif act == 'fold':
					currentPlayer.is_out = True
					folded+= 1
					str_log = '{} folds'.format(currentPlayer.name)
					print(str_log)
					self.history[round_name].append(str_log)					


			if folded == self.nplayers - 1:
				# exiting round, updating pot size
				self.pot+= sum(contributed)
				self.history[round_name].append(self.pot)
				return [p for p in self.players if not p.is_out], contributed
						
			if p_idx == end_round_idx:
				done = True				
			else:
				_, currentPlayer = self.get_player_to_left(currentPlayer)

		# exiting round, updating pot size
		self.pot+= sum(contributed)
		self.history[round_name].append(self.pot)
		return [p for p in self.players if not p.is_out], contributed



	def turn(self):
		return self.flop(cc=1, round_name='turn')


	def river(self):
		return self.flop(cc=1, round_name='river')


def get_strongest_hand(player, community_cards):	
	combs = list(itertools.combinations(player.cards + community_cards, 5))
	hand_values = []
	hands = []

	for c in combs:
		hand = PokerHand(c)
		hands.append(hand)
		hand_type = hand.classify()		
		hand_values.append(PokerHand.hand_value[hand_type])
		
	max_val = max(hand_values)
	tied_hands = [hands[i] for i in range(len(hand_values)) if hand_values[i] == max_val]	

	if len(tied_hands) == 1:
		return tied_hands
	else:
		combs = list(itertools.combinations(tied_hands, 2))
		wins = {}

		for a, b in combs:
			winner = a.get_winner(b)
			wins[str(a)] = wins.get(str(a), 0) + winner
			wins[str(b)] = wins.get(str(b), 0) - winner

		max_val = max(wins.values())
		best = [h for h in tied_hands if wins[str(h)] == max_val]
		return best


def decide_winner(players, community_cards):
	strongest_hand = [get_strongest_hand(p, community_cards)[0] for p in players]	
	combs = list(itertools.combinations(strongest_hand, 2))
	wins = {}

	for a, b in combs:
		winner = a.get_winner(b)
		wins[str(a)] = wins.get(str(a), 0) + winner
		wins[str(b)] = wins.get(str(b), 0) - winner

	max_val = max(wins.values())
	winning_hands = [h for h in strongest_hand if wins[str(h)] == max_val]

	winners = [players[i] for i, hand in enumerate(strongest_hand) if hand in winning_hands]
	return winners


if __name__ == '__main__':
	match = PokerMatch([HumanPlayer('Fernando Mir'), AIPlayer('AI-1'), AIPlayer('AI-2')])

	for _ in range(100):
		print('======'*20)
		players, x = match.preflop()
		
		if len(players) > 1:			
			players, x = match.flop(3, 'flop')
		else:
			print('Winner: {}'.format(players[0].name))
			match.rotate()
			continue
						
		if len(players) > 1:			
			players, x = match.turn()
		else:
			print('Winner: {}'.format(players[0].name))
			match.rotate()
			continue		
						
		if len(players) > 1:			
			players, x = match.river()

			if len(players) > 1:
				winners = decide_winner(match.players, match.communityCards)								

				for p in match.players:
					print('{} cards:'.format(p.name))
					print([str(c) for c in p.cards])

				print('Winners:')
				print([str(winner) for winner in winners])
			else:
				print('Winner: {}'.format(players[0].name))
				match.rotate()
				continue
		else:
			print('Winner: {}'.format(players[0].name))
			match.rotate()
			continue

							
		print(match.history)
		match.rotate()		
	
