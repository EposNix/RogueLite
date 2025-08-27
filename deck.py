import random
from collections import deque

class Deck:
    def __init__(self, cards=None):
        self.cards = list(cards) if cards else []
        self.hand = []
        self.discard_pile = []
        self.burned_pile = []  # Cards that are permanently removed from combat
        
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def draw(self, count=1):
        """Draw cards from deck to hand"""
        drawn = []
        for _ in range(count):
            if not self.cards:
                self._reshuffle_discard()
            
            if self.cards:
                card = self.cards.pop()
                self.hand.append(card)
                drawn.append(card)
        
        return drawn
    
    def draw_row(self, size=4):
        """Draw a new row of cards, burning any existing hand cards"""
        # Burn existing hand (default behavior)
        self.burn_hand()
        
        # Draw new row
        return self.draw(size)
    
    def discard(self, card):
        """Move card from hand to discard pile"""
        if card in self.hand:
            self.hand.remove(card)
            card.reset_modifiers()  # Reset any temporary modifiers
            self.discard_pile.append(card)
    
    def discard_hand(self):
        """Discard all cards in hand"""
        for card in self.hand[:]:  # Copy to avoid modification during iteration
            self.discard(card)
    
    def burn(self, card):
        """Permanently remove card from combat (exile)"""
        if card in self.hand:
            self.hand.remove(card)
        elif card in self.discard_pile:
            self.discard_pile.remove(card)
        elif card in self.cards:
            self.cards.remove(card)
        
        card.reset_modifiers()
        self.burned_pile.append(card)
    
    def burn_hand(self):
        """Burn all cards currently in hand"""
        for card in self.hand[:]:  # Copy to avoid modification during iteration
            self.burn(card)
    
    def _reshuffle_discard(self):
        """Shuffle discard pile back into deck"""
        if self.discard_pile:
            self.cards.extend(self.discard_pile)
            self.discard_pile.clear()
            self.shuffle()
    
    def get_hand_size(self):
        """Get current hand size"""
        return len(self.hand)
    
    def get_deck_size(self):
        """Get remaining cards in deck"""
        return len(self.cards)
    
    def get_discard_size(self):
        """Get cards in discard pile"""
        return len(self.discard_pile)
    
    def get_total_cards(self):
        """Get total cards available (deck + discard, excluding burned)"""
        return len(self.cards) + len(self.discard_pile)
    
    def add_card(self, card):
        """Add a new card to the deck (for card rewards)"""
        self.discard_pile.append(card)
    
    def remove_card(self, card_name):
        """Permanently remove a card from the deck (for card removal)"""
        # Try to remove from deck first
        for card in self.cards[:]:
            if card.name == card_name:
                self.cards.remove(card)
                return True
        
        # Then try discard pile
        for card in self.discard_pile[:]:
            if card.name == card_name:
                self.discard_pile.remove(card)
                return True
        
        return False
    
    def get_all_cards(self):
        """Get all cards in deck + discard (excluding burned)"""
        return self.cards + self.discard_pile
    
    def peek_next(self, count=1):
        """Peek at next cards without drawing them"""
        if len(self.cards) < count:
            self._reshuffle_discard()
        
        return self.cards[-count:] if self.cards else []