import random
from collections import Counter

class Card(object):
	def __init__(self, value, suit):
		self.value = value
		self.suit = suit		
		Card.SUIT_STR = {'Clubs': '\u2663', 'Hearts': '\u2665', 'Diamonds': '\u2666', 'Spades': '\u2660'}
		Card.VALUE_STR = {1:'A', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'J', 12:'Q', 13:'K'}

	def __eq__(self, other):
		return self.value == other.value

	def __str__(self):		
		return '{}{}'.format(Card.VALUE_STR[self.value], Card.SUIT_STR[self.suit])

	
class PokerCard(Card):
	def __init__(self, value, suit):
		super().__init__(value, suit)

	def __gt__(self, other):
		if self.value == 1 and other.value != 1:
			return True
		elif other.value == 1 and self.value != 1:
			return False
		else:
			return self.value > other.value
			

class PokerDeck(object):
	def __init__(self):
		self.cards = []
		values = range(1, 14)
		suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']

		for v in values:
			for s in suits:
				self.cards.append(PokerCard(v, s))
		
		self.shuffle()


	def has_cards(self):
		return len(self.cards) > 0


	def pick(self):
		if self.has_cards():
			return self.cards.pop()
		else:
			return None


	def shuffle(self):
		random.shuffle(self.cards)


class PokerHand(object):
	def __init__(self, cards):
		assert len(cards) == 5, 'Poker hand should have 5 cards'
		self.cards = sorted([PokerCard(c.value, c.suit) for c in cards])
		PokerHand.hand_value = {'Royal flush': 10, 'Straight flush': 9, 'Four of a kind': 8, 'Full house': 7,
								'Flush': 6, 'Straight': 5, 'Three of a kind': 4, 'Two pair': 3, 'Pair': 2, 'High card': 1}

		self.hand = self.classify()


	def get_winner(self, other):
		if PokerHand.hand_value[self.hand] > PokerHand.hand_value[other.hand]:
			return 1
		elif PokerHand.hand_value[self.hand] < PokerHand.hand_value[other.hand]:
			return -1
		elif PokerHand.hand_value[self.hand] == PokerHand.hand_value[other.hand]:
			# High card
			if self.hand == 'High card':
				cards_a = sorted(self.cards, reverse=True)
				cards_b = sorted(other.cards, reverse=True)				

				for a, b in zip(cards_a, cards_b):
					if a > b:
						return 1
					elif a < b:
						return -1
				return 0

			# Pair
			elif self.hand == 'Pair':
				counter_hand = Counter([c.value for c in self.cards])
				pair_hand = [k for k, v in counter_hand.items() if v==2][0]

				counter_other = Counter([c.value for c in other.cards])
				pair_other = [k for k, v in counter_other.items() if v==2][0]

				if PokerCard(pair_hand, '-') > PokerCard(pair_other, '-'):
					return 1
				elif PokerCard(pair_hand, '-') < PokerCard(pair_other, '-'):
					return -1				
				else:
					kickers_hand = sorted([PokerCard(c.value, '-') for c in self.cards if c.value != pair_hand], reverse=True)
					kickers_other = sorted([PokerCard(c.value, '-') for c in other.cards if c.value != pair_other], reverse=True)

					for a, b in zip(kickers_hand, kickers_other):
						if a > b:
							return 1
						elif a < b:
							return -1
					return 0
			# Two pair
			elif self.hand == 'Two pair':
				counter_hand = Counter([c.value for c in self.cards])				
				pairs_hand = sorted([PokerCard(k, '-') for k, v in counter_hand.items() if v==2], reverse=True)

				counter_other = Counter([c.value for c in other.cards])
				pairs_other = sorted([PokerCard(k, '-') for k, v in counter_other.items() if v==2], reverse=True)

				for a, b in zip(pairs_hand, pairs_other):
					if a > b:
						return 1
					elif a < b:
						return -1

				kicker_hand = [PokerCard(k, '-') for k, v in counter_hand.items() if v!=2]
				kicker_other = [PokerCard(k, '-') for k, v in counter_other.items() if v!=2]
				if PokerCard(kicker_hand, '-') > PokerCard(kicker_other, '-'):
					return 1
				elif PokerCard(kicker_hand, '-') < PokerCard(kicker_other, '-'):
					return -1
				return 0

			# Three of a kind
			elif self.hand == 'Three of a kind':
				counter_hand = Counter([c.value for c in self.cards])
				three_hand = [k for k, v in counter_hand.items() if v==3][0]

				counter_other = Counter([c.value for c in other.cards])
				three_other = [k for k, v in counter_other.items() if v==3][0]

				if PokerCard(three_hand, '-') > PokerCard(three_other, '-'):
					return 1
				elif PokerCard(three_hand, '-') < PokerCard(three_other, '-'):
					return -1

				kicker_hand = sorted([PokerCard(k, '-') for k, v in counter_hand.items() if v!=3], reverse=True)
				kicker_other = sorted([PokerCard(k, '-') for k, v in counter_other.items() if v!=3], reverse=True)

				for a, b in zip(kicker_hand, kicker_other):
					if a > b:
						return 1
					elif a < b:
						return -1
				return 0
			
			elif self.hand == 'Straight flush' or self.hand == 'Straight':
				if max(self.cards) > max(other.cards):
					return 1
				elif max(self.cards) < max(other.cards):
					return -1
				return 0

			elif self.hand == 'Flush':
				my_hand = sorted([PokerCard(c.value, '') for c in self.cards], reverse=True)
				other_hand = sorted([PokerCard(c.value, '') for c in other.cards], reverse=True)

				for a, b in zip(my_hand, other_hand):
					if a > b:
						return 1
					elif a < b:
						return -1
				return 0

			elif self.hand == 'Full house':
				counter_hand = Counter([c.value for c in self.cards])
				counter_other = Counter([c.value for c in other.cards])

				for rep in [3, 2]:
					my_hand = [k for k, v in counter_hand.items() if v==rep][0]			
					other_hand = [k for k, v in counter_other.items() if v==rep][0]
					if PokerCard(my_hand, '') > PokerCard(other_hand, ''):
						return 1
					elif PokerCard(my_hand, '') < PokerCard(other_hand, ''):
						return -1
				return 0

			elif self.hand == 'Four of a kind' or self.hand == 'Royal flush':
				return 0



	def classify(self):
		n_suits = len(set(c.suit for c in self.cards))
		cards = self.cards

		is_royal = False
		is_straight = False
				
		if cards[-1].value == 1 and cards[0].value == 10 and all([(cards[i + 1].value - cards[i].value) == 1 for i in range(3)]):
			is_royal = True
			is_straight = True		
		elif cards[-1].value == 1 and cards[0].value == 2 and all([(cards[i + 1].value - cards[i].value) == 1 for i in range(3)]):
			is_straight = True		
		elif all([(cards[i + 1].value - cards[i].value) == 1 for i in range(4)]):
			is_straight = True


		# Straight or Royal Flush
		if n_suits == 1:
			if is_straight and is_royal:			
				return 'Royal flush'
			elif is_straight:
				return 'Straight flush'
		elif is_straight:
			return 'Straight'
		

		rank_counter = Counter([c.value for c in cards])		

		if max(rank_counter.values()) == 4:
			return 'Four of a kind'
		elif max(rank_counter.values()) == 3 and min(rank_counter.values()) == 2:
			return 'Full house'		
		elif n_suits == 1:
			return 'Flush'
		elif max(rank_counter.values()) == 3:
			return 'Three of a kind'
		elif sum(v == 2 for s, v in rank_counter.items()) == 2:
			return 'Two pair'
		elif max(rank_counter.values()) == 2:
			return 'Pair'
		else:
			return 'High card'


	def __str__(self):
		return ', '.join([str(c) for c in self.cards])


	@staticmethod
	def random_hand():
		deck = PokerDeck()
		return PokerHand([deck.pick() for _ in range(5)])


if __name__ == '__main__':
	hands = []
	for _ in range(10000):
		hands.append(PokerHand.random_hand().classify())
	print(Counter(hands))
	
	

