import pygame
import re
from enum import Enum
from card import CardType

class CombatPhase(Enum):
    SHOW = 1      # Drawing cards face-up
    SCHEME = 2    # Player selecting card and prediction
    COMMIT = 3    # Enemy AI choosing
    REVEAL = 4    # Showing choices and resolving
    CLEANUP = 5   # End of beat effects

class Combat:
    def __init__(self, player_deck, enemy):
        self.player_deck = player_deck
        self.enemy = enemy
        self.phase = CombatPhase.SHOW
        
        # Player state
        self.player_hp = 75
        self.player_max_hp = 75
        self.player_focus = 0
        self.player_guard = 0
        self.player_status_effects = {}
        
        # Beat state
        self.player_selected_card = None
        self.player_prediction_slot = None  # 0-3 for enemy slots A-D
        self.enemy_chosen_card = None
        self.enemy_chosen_slot = None
        
        # Resolution state
        self.resolution_log = []
        self.beat_number = 1
        
        # UI state
        self.card_width = 150
        self.card_height = 100
        self.card_spacing = 10
        
        # Start first beat
        self._start_new_beat()
    
    def _start_new_beat(self):
        """Start a new combat beat"""
        self.phase = CombatPhase.SHOW
        
        # Reset beat effects
        self.player_guard = 0
        self.enemy.reset_beat_effects()
        
        # Draw new rows
        self.player_deck.draw_row(4)
        self.enemy.deck.draw_row(4)
        
        # Clear selections
        self.player_selected_card = None
        self.player_prediction_slot = None
        self.enemy_chosen_card = None
        self.enemy_chosen_slot = None
        
        # Clear resolution log
        self.resolution_log.clear()
        
        self.phase = CombatPhase.SCHEME
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.phase == CombatPhase.SCHEME:
                self._handle_card_selection(event.pos)
                self._handle_prediction_selection(event.pos)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.phase == CombatPhase.SCHEME:
                if self.player_selected_card and self.player_prediction_slot is not None:
                    self._commit_phase()
            elif event.key == pygame.K_RETURN and self.phase == CombatPhase.REVEAL:
                self._cleanup_phase()
    
    def _handle_card_selection(self, mouse_pos):
        """Handle player clicking on their cards"""
        for i, card in enumerate(self.player_deck.hand):
            if card.contains_point(mouse_pos):
                self.player_selected_card = card
                break
    
    def _handle_prediction_selection(self, mouse_pos):
        """Handle player clicking on enemy cards to predict"""
        for i, card in enumerate(self.enemy.deck.hand):
            if card.contains_point(mouse_pos):
                self.player_prediction_slot = i
                break
    
    def _commit_phase(self):
        """Move to commit phase - enemy AI chooses"""
        self.phase = CombatPhase.COMMIT
        
        # Enemy AI chooses card
        self.enemy_chosen_card = self.enemy.choose_card(self.player_deck.hand)
        if self.enemy_chosen_card:
            self.enemy_chosen_slot = self.enemy.deck.hand.index(self.enemy_chosen_card)
        
        self.phase = CombatPhase.REVEAL
        self._resolve_beat()
    
    def _resolve_beat(self):
        """Resolve the combat beat"""
        if not self.player_selected_card or not self.enemy_chosen_card:
            return
        
        # Check for correct prediction
        read_bonus = False
        if self.player_prediction_slot == self.enemy_chosen_slot:
            read_bonus = True
            self.player_selected_card.apply_read_bonus()
            self.resolution_log.append("✓ Correct prediction! Read bonus applied.")
        else:
            self.resolution_log.append("✗ Incorrect prediction.")
        
        # Apply Feint swaps first (before speed comparison)
        self._handle_feints()
        
        # Determine resolution order by speed
        player_speed = self.player_selected_card.get_effective_speed()
        enemy_speed = self.enemy_chosen_card.get_effective_speed()
        
        if player_speed > enemy_speed:
            self._resolve_card_effects(True)  # Player first
        elif enemy_speed > player_speed:
            self._resolve_card_effects(False)  # Enemy first
        else:
            # Speed tie - handle clash
            self._resolve_clash()
    
    def _handle_feints(self):
        """Handle Feint card swaps"""
        if self.player_selected_card.name == "Feint":
            # Allow player to swap with an unplayed card (simplified for now)
            unplayed = [c for c in self.player_deck.hand if c != self.player_selected_card]
            if unplayed:
                # For now, just swap with first unplayed card
                swap_card = unplayed[0]
                self.player_selected_card = swap_card
                swap_card.speed_modifier = max(0, 5 - swap_card.base_speed)  # Resolves at S5
                self.resolution_log.append(f"Feint: Swapped to {swap_card.name} (S5)")
    
    def _resolve_card_effects(self, player_first):
        """Resolve card effects in speed order"""
        if player_first:
            self._resolve_player_card()
            if not self.enemy.stunned:
                self._resolve_enemy_card()
        else:
            self._resolve_enemy_card()
            if not self._is_player_stunned():
                self._resolve_player_card()
    
    def _resolve_player_card(self):
        """Resolve player's selected card"""
        card = self.player_selected_card
        
        # Check if card can counter/intercept enemy
        if card.type == CardType.COUNTER and self.enemy_chosen_card.type == CardType.ATTACK:
            if card.get_effective_speed() >= self.enemy_chosen_card.get_effective_speed():
                self.enemy.stunned = True
                self.resolution_log.append(f"Counter: {card.name} cancels {self.enemy_chosen_card.name}")
        
        if card.type == CardType.DODGE:
            if self.enemy_chosen_card.type in [CardType.ATTACK, CardType.GRAPPLE]:
                self.resolution_log.append(f"Dodge: {card.name} avoids {self.enemy_chosen_card.name}")
                return  # Dodge successful, no damage taken
        
        # Apply card effects
        damage = card.get_effective_damage()
        if damage > 0:
            ignore_guard = "ignore guard" in card.effect.lower()
            if ignore_guard:
                self.enemy.hp = max(0, self.enemy.hp - damage)
                actual_damage = damage
                self.resolution_log.append(f"Player deals {actual_damage} damage (ignores guard)")
            else:
                actual_damage = self.enemy.take_damage(damage)
                self.resolution_log.append(f"Player deals {actual_damage} damage")
            
            # Check if damage stuns enemy
            if actual_damage >= self.enemy_chosen_card.get_effective_stability():
                self.enemy.stunned = True
                self.resolution_log.append("Enemy stunned!")
        
        # Handle special effects
        self._apply_card_special_effects(card, True)
    
    def _resolve_enemy_card(self):
        """Resolve enemy's chosen card"""
        card = self.enemy_chosen_card
        
        # Apply card effects
        damage = card.get_effective_damage()
        if damage > 0:
            ignore_guard = "ignore guard" in card.effect.lower()
            if not ignore_guard and self.player_guard > 0:
                blocked = min(self.player_guard, damage)
                damage -= blocked
                self.player_guard -= blocked
                if blocked > 0:
                    self.resolution_log.append(f"Blocked {blocked} damage")

            if damage > 0:
                self.player_hp -= damage
                self.player_hp = max(0, self.player_hp)
                if ignore_guard:
                    self.resolution_log.append(f"Enemy deals {damage} damage (ignores guard)")
                else:
                    self.resolution_log.append(f"Enemy deals {damage} damage")

                # Check if damage stuns player
                if damage >= self.player_selected_card.get_effective_stability():
                    self.resolution_log.append("Player stunned!")
        
        # Handle special effects
        self._apply_card_special_effects(card, False)
    
    def _apply_card_special_effects(self, card, is_player):
        """Apply special card effects beyond basic damage"""
        effect_text = card.effect.lower()

        # Guard or Prevent
        guard_match = re.search(r'prevent\s+(\d+)', effect_text)
        if card.type == CardType.GUARD or guard_match:
            guard_amount = int(guard_match.group(1)) if guard_match else 0
            if is_player:
                self.player_guard += guard_amount
                self.resolution_log.append(f"Player gains {guard_amount} guard")
            else:
                self.enemy.add_guard(guard_amount)
                self.resolution_log.append(f"Enemy gains {guard_amount} guard")

        # Grapple always stuns
        if card.type == CardType.GRAPPLE:
            if is_player:
                self.enemy.stunned = True
                self.resolution_log.append("Grapple: Enemy stunned")
            else:
                self.resolution_log.append("Grapple: Player stunned")

        # Simple healing prep cards
        if card.type == CardType.PREP and "heal" in effect_text:
            if is_player:
                self.player_hp = min(self.player_max_hp, self.player_hp + 2)
                self.resolution_log.append("Player heals 2 HP")
            else:
                self.enemy.heal(2)
                self.resolution_log.append("Enemy heals 2 HP")

        # Bleed effects
        bleed_match = re.search(r'bleed\s+(\d+)(?:\s*\((\d+) beats?\))?', effect_text)
        if bleed_match:
            bleed_amount = int(bleed_match.group(1))
            bleed_duration = int(bleed_match.group(2)) if bleed_match.group(2) else 2
            if is_player:
                self.enemy.add_status_effect("bleed", bleed_amount, bleed_duration)
                self.resolution_log.append(f"Enemy gains Bleed {bleed_amount}")
            else:
                self.player_status_effects["bleed"] = bleed_amount
                self.player_status_effects["bleed_duration"] = bleed_duration
                self.resolution_log.append(f"Player gains Bleed {bleed_amount}")
    
    def _resolve_clash(self):
        """Handle speed tie with clash rules"""
        player_clash = self.player_selected_card.clash
        enemy_clash = self.enemy_chosen_card.clash
        
        if "both take" in player_clash.lower():
            # Extract damage amount
            import re
            match = re.search(r'both take (\d+)', player_clash.lower())
            if match:
                clash_damage = int(match.group(1))
                self.player_hp -= clash_damage
                self.enemy.take_damage(clash_damage)
                self.resolution_log.append(f"Clash: Both take {clash_damage} damage")
        
        # Both cards still resolve their effects
        self._resolve_player_card()
        self._resolve_enemy_card()
    
    def _is_player_stunned(self):
        """Check if player is stunned (simplified)"""
        return False  # Would need proper stun tracking
    
    def _cleanup_phase(self):
        """Clean up after beat resolution"""
        self.phase = CombatPhase.CLEANUP
        
        # Discard played cards
        if self.player_selected_card:
            self.player_deck.discard(self.player_selected_card)
        if self.enemy_chosen_card:
            self.enemy.deck.discard(self.enemy_chosen_card)
        
        # Burn remaining cards
        self.player_deck.burn_hand()
        self.enemy.deck.burn_hand()
        
        # Apply status effects
        self._apply_end_beat_status_effects()
        
        # Check win/loss conditions
        if self.player_hp <= 0:
            self.resolution_log.append("DEFEAT!")
            return
        elif self.enemy.hp <= 0:
            self.resolution_log.append("VICTORY!")
            return
        
        # Start next beat
        self.beat_number += 1
        self._start_new_beat()
    
    def _apply_end_beat_status_effects(self):
        """Apply status effects at end of beat"""
        # Player status effects
        if "bleed" in self.player_status_effects:
            bleed_dmg = self.player_status_effects["bleed"]
            self.player_hp -= bleed_dmg
            self.resolution_log.append(f"Player bleeds for {bleed_dmg}")
            
            self.player_status_effects["bleed_duration"] -= 1
            if self.player_status_effects["bleed_duration"] <= 0:
                del self.player_status_effects["bleed"]
                del self.player_status_effects["bleed_duration"]
        
        # Enemy status effects
        self.enemy.apply_status_effects()
    
    def update(self, dt):
        """Update combat state"""
        pass
    
    def draw(self, screen, font, big_font):
        """Draw the combat interface"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        RED = (255, 100, 100)
        BLUE = (100, 100, 255)
        GREEN = (100, 255, 100)
        GRAY = (128, 128, 128)
        
        # Draw enemy area (top)
        enemy_y = 50
        
        # Enemy info
        enemy_text = big_font.render(f"{self.enemy.name} - HP: {self.enemy.hp}/{self.enemy.max_hp}", True, WHITE)
        screen.blit(enemy_text, (20, 20))
        
        if self.enemy.get_status_display():
            status_text = font.render(self.enemy.get_status_display(), True, RED)
            screen.blit(status_text, (20, 50))
        
        # Enemy cards
        enemy_hand = self.enemy.deck.hand
        enemy_start_x = (screen_width - (len(enemy_hand) * (self.card_width + self.card_spacing))) // 2
        
        for i, card in enumerate(enemy_hand):
            x = enemy_start_x + i * (self.card_width + self.card_spacing)
            
            # Highlight if this is the prediction slot
            highlighted = (self.player_prediction_slot == i)
            
            # Show if this was chosen by enemy (in reveal phase)
            selected = (self.phase == CombatPhase.REVEAL and 
                       self.enemy_chosen_card and card == self.enemy_chosen_card)
            
            card.draw(screen, x, enemy_y, self.card_width, self.card_height, 
                     font, selected, highlighted)
            
            # Draw slot labels
            slot_label = font.render(chr(65 + i), True, WHITE)  # A, B, C, D
            screen.blit(slot_label, (x + self.card_width//2 - 5, enemy_y - 20))
        
        # Draw player area (bottom)
        player_y = screen_height - self.card_height - 100
        
        # Player info
        player_text = big_font.render(f"Player - HP: {self.player_hp}/{self.player_max_hp}", True, WHITE)
        screen.blit(player_text, (20, screen_height - 180))
        
        if self.player_focus > 0:
            focus_text = font.render(f"Focus: {self.player_focus}", True, BLUE)
            screen.blit(focus_text, (20, screen_height - 160))
        
        if self.player_guard > 0:
            guard_text = font.render(f"Guard: {self.player_guard}", True, GREEN)
            screen.blit(guard_text, (120, screen_height - 160))
        
        # Player cards
        player_hand = self.player_deck.hand
        player_start_x = (screen_width - (len(player_hand) * (self.card_width + self.card_spacing))) // 2
        
        for i, card in enumerate(player_hand):
            x = player_start_x + i * (self.card_width + self.card_spacing)
            
            selected = (card == self.player_selected_card)
            
            card.draw(screen, x, player_y, self.card_width, self.card_height, 
                     font, selected, False)
        
        # Draw phase info
        phase_text = font.render(f"Phase: {self.phase.name} | Beat: {self.beat_number}", True, WHITE)
        screen.blit(phase_text, (screen_width - 200, 20))
        
        # Draw instructions based on phase
        if self.phase == CombatPhase.SCHEME:
            if not self.player_selected_card:
                instruction = "Click a card to select"
            elif self.player_prediction_slot is None:
                instruction = "Click enemy card to predict"
            else:
                instruction = "Press SPACE to commit"
            
            inst_text = font.render(instruction, True, WHITE)
            screen.blit(inst_text, (screen_width//2 - inst_text.get_width()//2, screen_height//2))
        
        elif self.phase == CombatPhase.REVEAL:
            inst_text = font.render("Press ENTER to continue", True, WHITE)
            screen.blit(inst_text, (screen_width//2 - inst_text.get_width()//2, screen_height//2))
        
        # Draw resolution log
        if self.resolution_log:
            log_y = screen_height//2 + 50
            for i, log_entry in enumerate(self.resolution_log[-5:]):  # Show last 5 entries
                log_text = font.render(log_entry, True, WHITE)
                screen.blit(log_text, (20, log_y + i * 20))
        
        # Draw prediction indicator
        if self.player_prediction_slot is not None:
            pred_text = font.render(f"Predicting: {chr(65 + self.player_prediction_slot)}", True, WHITE)
            screen.blit(pred_text, (screen_width - 200, 50))