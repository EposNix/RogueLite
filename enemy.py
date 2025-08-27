from deck import Deck
import random
import math

class Enemy:
    def __init__(self, name, hp, deck, archetype="Neutral"):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.deck = deck
        self.archetype = archetype
        
        # AI parameters
        self.temperature = 0.8  # Controls randomness (lower = more predictable)
        self.last_played_card = None
        self.anti_repeat_penalty = 0.3
        
        # Status effects
        self.focus = 0
        self.status_effects = {}  # e.g., {"bleed": 2, "slow": 1}
        
        # Combat state
        self.guard_amount = 0  # Damage prevention this beat
        self.stunned = False
        
    def take_damage(self, amount):
        """Take damage, accounting for guard"""
        if self.guard_amount > 0:
            blocked = min(self.guard_amount, amount)
            amount -= blocked
            self.guard_amount -= blocked
        
        self.hp -= amount
        self.hp = max(0, self.hp)
        return amount  # Return actual damage taken
    
    def heal(self, amount):
        """Heal HP"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def add_guard(self, amount):
        """Add guard (damage prevention) for this beat"""
        self.guard_amount += amount
    
    def reset_beat_effects(self):
        """Reset per-beat effects like guard"""
        self.guard_amount = 0
        self.stunned = False
    
    def apply_status_effects(self):
        """Apply ongoing status effects at end of beat"""
        damage_taken = 0
        
        if "bleed" in self.status_effects:
            bleed_damage = self.status_effects["bleed"]
            damage_taken += self.take_damage(bleed_damage)
        
        # Reduce status effect durations (simplified - using turn counters)
        for effect in list(self.status_effects.keys()):
            if effect.endswith("_duration"):
                self.status_effects[effect] -= 1
                if self.status_effects[effect] <= 0:
                    # Remove the effect
                    base_effect = effect.replace("_duration", "")
                    if base_effect in self.status_effects:
                        del self.status_effects[base_effect]
                    del self.status_effects[effect]
        
        return damage_taken
    
    def add_status_effect(self, effect, amount, duration=2):
        """Add a status effect"""
        self.status_effects[effect] = amount
        self.status_effects[f"{effect}_duration"] = duration
    
    def is_alive(self):
        """Check if enemy is still alive"""
        return self.hp > 0
    
    def choose_card(self, player_hand):
        """AI card selection using mixed strategy"""
        available_cards = self.deck.hand
        if not available_cards:
            return None
        
        # Calculate payoff matrix
        payoffs = []
        for enemy_card in available_cards:
            card_payoffs = []
            for player_card in player_hand:
                payoff = self._calculate_payoff(enemy_card, player_card)
                card_payoffs.append(payoff)
            
            # Average payoff assuming player uses mixed strategy
            avg_payoff = sum(card_payoffs) / len(card_payoffs)
            payoffs.append(avg_payoff)
        
        # Apply anti-repeat penalty
        if self.last_played_card:
            for i, card in enumerate(available_cards):
                if card.name == self.last_played_card.name:
                    payoffs[i] -= self.anti_repeat_penalty
        
        # Convert to softmax distribution
        probabilities = self._softmax(payoffs, self.temperature)
        
        # Sample from distribution
        chosen_index = self._weighted_random_choice(probabilities)
        chosen_card = available_cards[chosen_index]
        
        self.last_played_card = chosen_card
        return chosen_card
    
    def _calculate_payoff(self, my_card, opponent_card):
        """Calculate expected payoff for playing my_card vs opponent_card"""
        payoff = 0
        
        # Base damage value
        if my_card.get_effective_damage() > 0:
            payoff += my_card.get_effective_damage()
        
        # Speed advantage bonus
        if my_card.get_effective_speed() > opponent_card.get_effective_speed():
            payoff += 1  # Acting first is valuable
        
        # Counter/defensive bonuses
        if my_card.can_counter(opponent_card):
            payoff += 2  # Successfully countering is valuable
        
        # Type matchup bonuses
        if opponent_card.type.value in ["Attack", "Grapple"] and my_card.type.value == "Guard":
            payoff += 1
        
        # Survival considerations
        expected_incoming_damage = opponent_card.get_effective_damage()
        if expected_incoming_damage >= my_card.get_effective_stability():
            payoff -= 2  # Getting stunned is bad
        
        # HP-based adjustments
        if self.hp < self.max_hp * 0.3:  # Low HP, play more defensively
            if my_card.type.value in ["Guard", "Dodge"]:
                payoff += 1
        
        return payoff
    
    def _softmax(self, values, temperature):
        """Convert values to probability distribution using softmax"""
        if not values:
            return []
        
        # Subtract max for numerical stability
        max_val = max(values)
        exp_values = [math.exp((v - max_val) / temperature) for v in values]
        sum_exp = sum(exp_values)
        
        return [exp_val / sum_exp for exp_val in exp_values]
    
    def _weighted_random_choice(self, probabilities):
        """Choose index based on probability weights"""
        r = random.random()
        cumulative = 0
        
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return i
        
        return len(probabilities) - 1  # Fallback to last index
    
    def get_status_display(self):
        """Get string representation of status effects"""
        if not self.status_effects:
            return ""
        
        statuses = []
        for effect, value in self.status_effects.items():
            if not effect.endswith("_duration"):
                statuses.append(f"{effect.title()}: {value}")
        
        return " | ".join(statuses)