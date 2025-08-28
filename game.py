import pygame
from enum import Enum
from combat import Combat
from card import Card, CardType
from deck import Deck
from enemies import create_enemy
from map_system import MapSystem, NodeType

class GameState(Enum):
    MENU = 1
    COMBAT = 2
    MAP = 3
    SHOP = 4
    EVENT = 5
    CAMP = 6
    TREASURE = 7

class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.state = GameState.MAP  # Start with map view
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.BLUE = (100, 150, 255)
        self.RED = (255, 100, 100)
        self.GREEN = (100, 255, 100)
        self.YELLOW = (255, 255, 100)
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        # Initialize game systems
        self._init_starting_deck()
        self.map_system = MapSystem()
        self.combat = None
    
    def _init_starting_deck(self):
        """Create the starting deck based on Appendix A"""
        cards = []
        
        # Create 2 copies of each starter card
        starter_cards = [
            ("Quick Jab", CardType.ATTACK, 5, 1, 1, "Deal 1", "Read: +1 dmg", "Clash: both take 1"),
            ("Heavy Swing", CardType.ATTACK, 2, 4, 3, "Deal 4", "", "Clash: both take 2"),
            ("Lunge", CardType.ATTACK, 4, 2, 2, "Deal 2; if first, +1 dmg", "", ""),
            ("Guard Wall", CardType.GUARD, 1, 0, 4, "Prevent 4; if not hit, next beat +1 Speed", "", ""),
            ("Parry", CardType.COUNTER, 4, 2, 2, "If foe Attack and first, cancel it; deal 2", "", ""),
            ("Sidestep", CardType.DODGE, 6, 0, 1, "If foe Attack/Grapple, misses; Charge", "", "Clash: no effect"),
            ("Grapple", CardType.GRAPPLE, 3, 2, 2, "Deal 2; Stun even if dmg < Stability", "", ""),
            ("Choke Chain", CardType.GRAPPLE, 2, 1, 3, "Deal 1; Slow 1 next beat", "", ""),
            ("Disrupt", CardType.TRICK, 5, 1, 1, "Foe Slow 2 this beat; deal 1", "", ""),
            ("Focus", CardType.PREP, 2, 0, 3, "Heal 2; next beat +1 Stability", "Effect: heal", ""),
            ("Ignite", CardType.SKILL, 3, 1, 2, "Deal 1; Bleed 1 (2 beats)", "Read: +Bleed 1", ""),
            ("Feint", CardType.TRICK, 6, 1, 1, "After reveal, swap with unplayed; resolves S5", "Read: +1 dmg", ""),
            ("Piercing Strike", CardType.ATTACK, 3, 3, 2, "Deal 3; Ignore guard", "", ""),
            ("Deep Cut", CardType.ATTACK, 4, 1, 2, "Deal 1; Bleed 2 (3 beats)", "Read: +1 dmg", ""),
            ("Reinforce", CardType.GUARD, 2, 0, 4, "Prevent 6", "", "")
        ]
        
        for name, card_type, speed, damage, stability, effect, read, clash in starter_cards:
            for _ in range(2):  # 2 copies each
                cards.append(Card(name, card_type, speed, damage, stability, effect, read, clash))
        
        self.player_deck = Deck(cards)
    
    def _init_combat(self):
        """Initialize combat with a basic enemy"""
        # Create a simple enemy with similar cards
        enemy_cards = []
        enemy_data = [
            ("Quick Maul", CardType.ATTACK, 5, 2, 1, "Deal 2", "", ""),
            ("Heavy Chomp", CardType.ATTACK, 2, 4, 3, "Deal 4", "", ""),
            ("Guard", CardType.GUARD, 1, 0, 4, "Prevent 3", "", ""),
            ("Howl", CardType.PREP, 3, 0, 2, "Charge", "", "")
        ]
        
        for name, card_type, speed, damage, stability, effect, read, clash in enemy_data:
            for _ in range(3):  # 3 copies each for variety
                enemy_cards.append(Card(name, card_type, speed, damage, stability, effect, read, clash))
        
        enemy_deck = Deck(enemy_cards)
        enemy = Enemy("Brawler Pup", 25, enemy_deck, "Bruiser")
        
        self.combat = Combat(self.player_deck, enemy)
    
    def handle_event(self, event):
        # Global escape key handling
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state in [GameState.SHOP, GameState.CAMP, GameState.EVENT, GameState.TREASURE]:
                self.state = GameState.MAP
        
        if self.state == GameState.COMBAT and self.combat:
            self.combat.handle_event(event)
        elif self.state == GameState.MAP:
            self._handle_map_event(event)
    
    def _handle_map_event(self, event):
        """Handle events on the map screen"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if player clicked on one of the 3 node choices
            choices = self.map_system.get_current_choices()
            if choices:
                # Simple button layout - 3 buttons centered
                button_width = 200
                button_height = 80
                button_spacing = 20
                start_x = (self.width - (3 * button_width + 2 * button_spacing)) // 2
                start_y = self.height // 2
                
                for i, node in enumerate(choices):
                    button_x = start_x + i * (button_width + button_spacing)
                    button_rect = pygame.Rect(button_x, start_y, button_width, button_height)
                    
                    if button_rect.collidepoint(event.pos):
                        self._choose_node(i)
                        break
    
    def _choose_node(self, node_index):
        """Player chooses a node from the map"""
        chosen_node = self.map_system.choose_node(node_index)
        if chosen_node:
            # Handle different node types
            if chosen_node.type == NodeType.COMBAT:
                self._start_combat()
            elif chosen_node.type == NodeType.ELITE:
                self._start_combat(elite=True)
            elif chosen_node.type == NodeType.BOSS:
                self._start_combat(boss=True)
            elif chosen_node.type == NodeType.SHOP:
                self.state = GameState.SHOP
            elif chosen_node.type == NodeType.CAMP:
                self.state = GameState.CAMP
            elif chosen_node.type == NodeType.EVENT:
                self.state = GameState.EVENT
            elif chosen_node.type == NodeType.TREASURE:
                self.state = GameState.TREASURE
    
    def _start_combat(self, elite=False, boss=False):
        """Start a combat encounter"""
        act = self.map_system.current_act
        enemy = create_enemy(act, elite, boss)
        self.combat = Combat(self.player_deck, enemy)
        self.state = GameState.COMBAT
    
    def _end_combat(self):
        """Handle end of combat, return to map"""
        self.state = GameState.MAP
        self.combat = None
    
    def update(self, dt):
        if self.state == GameState.COMBAT and self.combat:
            self.combat.update(dt)
            # Check for combat completion
            if self.combat.player_hp <= 0 or self.combat.enemy.hp <= 0:
                # Add small delay before returning to map (could be improved)
                if hasattr(self, 'combat_end_timer'):
                    self.combat_end_timer -= dt
                    if self.combat_end_timer <= 0:
                        self._end_combat()
                        del self.combat_end_timer
                else:
                    self.combat_end_timer = 2.0  # 2 second delay
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        if self.state == GameState.COMBAT and self.combat:
            self.combat.draw(self.screen, self.font, self.big_font)
        elif self.state == GameState.MAP:
            self._draw_map()
        elif self.state in [GameState.SHOP, GameState.CAMP, GameState.EVENT, GameState.TREASURE]:
            self._draw_placeholder_screen()
        
        # Draw debug info
        debug_text = f"State: {self.state.name}"
        debug_surface = self.font.render(debug_text, True, self.WHITE)
        self.screen.blit(debug_surface, (10, 10))
    
    def _draw_map(self):
        """Draw the map screen with 3 node choices"""
        # Title
        title_text = self.big_font.render("Choose Your Path", True, self.WHITE)
        title_rect = title_text.get_rect(centerx=self.width//2, y=50)
        self.screen.blit(title_text, title_rect)
        
        # Progress indicator
        act, floor, total_floors = self.map_system.get_act_progress()
        progress_text = self.font.render(f"Act {act} - Floor {floor}/{total_floors}", True, self.WHITE)
        progress_rect = progress_text.get_rect(centerx=self.width//2, y=100)
        self.screen.blit(progress_text, progress_rect)
        
        # Draw the 3 node choices
        choices = self.map_system.get_current_choices()
        if choices:
            button_width = 200
            button_height = 80
            button_spacing = 20
            start_x = (self.width - (3 * button_width + 2 * button_spacing)) // 2
            start_y = self.height // 2
            
            for i, node in enumerate(choices):
                button_x = start_x + i * (button_width + button_spacing)
                button_rect = pygame.Rect(button_x, start_y, button_width, button_height)
                
                # Get node color based on type
                node_color = self._get_node_color(node.type)
                
                # Draw button
                pygame.draw.rect(self.screen, node_color, button_rect)
                pygame.draw.rect(self.screen, self.WHITE, button_rect, 2)
                
                # Draw icon
                icon_text = self.big_font.render(node.get_icon(), True, self.WHITE)
                icon_rect = icon_text.get_rect(centerx=button_x + button_width//2, y=start_y + 10)
                self.screen.blit(icon_text, icon_rect)
                
                # Draw node name
                name_text = self.font.render(node.get_display_name(), True, self.WHITE)
                name_rect = name_text.get_rect(centerx=button_x + button_width//2, y=start_y + 50)
                self.screen.blit(name_text, name_rect)
        
        # Draw gold
        gold_text = self.font.render(f"Gold: {self.map_system.gold}", True, self.YELLOW)
        self.screen.blit(gold_text, (self.width - 100, 20))
    
    def _get_node_color(self, node_type):
        """Get color for different node types"""
        colors = {
            NodeType.COMBAT: self.RED,
            NodeType.ELITE: (150, 0, 150),  # Dark Purple
            NodeType.BOSS: (200, 0, 0),     # Dark Red
            NodeType.EVENT: self.BLUE,
            NodeType.SHOP: self.GREEN,
            NodeType.CAMP: (255, 150, 0),   # Orange
            NodeType.TREASURE: self.YELLOW
        }
        return colors.get(node_type, self.GRAY)
    
    def _draw_placeholder_screen(self):
        """Draw placeholder for unimplemented screens"""
        text = f"{self.state.name} - Not Implemented"
        placeholder_text = self.big_font.render(text, True, self.WHITE)
        text_rect = placeholder_text.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(placeholder_text, text_rect)
        
        # Return to map instruction
        instruction = "Press ESCAPE to return to map"
        inst_text = self.font.render(instruction, True, self.WHITE)
        inst_rect = inst_text.get_rect(center=(self.width//2, self.height//2 + 50))
        self.screen.blit(inst_text, inst_rect)