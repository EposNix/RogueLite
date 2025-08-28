from enum import Enum
import pygame

class CardType(Enum):
    ATTACK = "Attack"
    GUARD = "Guard"
    COUNTER = "Counter"
    DODGE = "Dodge"
    GRAPPLE = "Grapple"
    TRICK = "Trick"
    PREP = "Prep"
    SKILL = "Skill"

class Card:
    def __init__(self, name, card_type, speed, damage, stability, effect="", read="", clash=""):
        self.name = name
        self.type = card_type
        self.speed = speed
        self.base_speed = speed
        self.damage = damage
        self.base_damage = damage
        self.stability = stability
        self.base_stability = stability
        self.effect = effect
        self.read = read
        self.clash = clash
        
        # Runtime modifiers
        self.speed_modifier = 0
        self.damage_modifier = 0
        self.stability_modifier = 0
        self.stunned = False
        self.read_triggered = False
        
        # Visual properties
        self.rect = None
        self.selected = False
        self.highlighted = False
    
    def get_effective_speed(self):
        return max(1, self.base_speed + self.speed_modifier)
    
    def get_effective_damage(self):
        return max(0, self.base_damage + self.damage_modifier)
    
    def get_effective_stability(self):
        return max(1, self.base_stability + self.stability_modifier)
    
    def apply_read_bonus(self):
        """Apply the read bonus if prediction was correct"""
        if not self.read_triggered and self.read:
            if "+1 dmg" in self.read:
                self.damage_modifier += 1
            if "+1 Speed" in self.read:
                self.speed_modifier += 1
            if "+Bleed" in self.read:
                # Handle bleed bonus (implementation depends on status system)
                pass
            self.read_triggered = True
    
    def reset_modifiers(self):
        """Reset all temporary modifiers"""
        self.speed_modifier = 0
        self.damage_modifier = 0
        self.stability_modifier = 0
        self.stunned = False
        self.read_triggered = False
    
    def can_counter(self, other_card):
        """Check if this card can counter another card"""
        if self.type == CardType.COUNTER:
            return other_card.type == CardType.ATTACK
        elif self.type == CardType.DODGE:
            return other_card.type in [CardType.ATTACK, CardType.GRAPPLE]
        return False
    
    def get_type_color(self):
        """Get color based on card type"""
        colors = {
            CardType.ATTACK: (255, 100, 100),     # Red
            CardType.GUARD: (100, 100, 255),      # Blue
            CardType.COUNTER: (255, 255, 100),    # Yellow
            CardType.DODGE: (100, 255, 100),      # Green
            CardType.GRAPPLE: (255, 100, 255),    # Magenta
            CardType.TRICK: (255, 150, 0),        # Orange
            CardType.PREP: (150, 150, 255),       # Light Blue
            CardType.SKILL: (200, 100, 255)       # Purple
        }
        return colors.get(self.type, (128, 128, 128))
    
    def draw(self, surface, x, y, width, height, font, selected=False, highlighted=False):
        """Draw the card on the surface"""
        # Basic background with type tint
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((245, 245, 245))
        tint = pygame.Surface((width, height), pygame.SRCALPHA)
        tint.fill(self.get_type_color() + (60,))
        bg.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.rect = pygame.Rect(x, y, width, height)
        surface.blit(bg, self.rect)

        # Border to show selection/highlight
        border_color = (255, 255, 255)
        if selected:
            border_color = (255, 215, 0)  # Gold when selected
        elif highlighted:
            border_color = (255, 255, 0)  # Yellow when predicting
        pygame.draw.rect(surface, border_color, self.rect, 4)

        # Use a larger font for the card name
        name_font = pygame.font.Font(None, font.get_height() + 8)
        name_text = name_font.render(self.name, True, (0, 0, 0))
        text_rect = name_text.get_rect(centerx=x + width//2, top=y + 15)
        surface.blit(name_text, text_rect)

        # Body font for stats and effects
        body_font = font

        # Speed indicator
        speed_text = body_font.render(f"S{self.get_effective_speed()}", True, (0, 0, 0))
        surface.blit(speed_text, (x + 10, y + 15))

        # Damage (if any)
        if self.get_effective_damage() > 0:
            dmg_text = body_font.render(f"{self.get_effective_damage()}", True, (0, 0, 0))
            surface.blit(dmg_text, (x + width - dmg_text.get_width() - 10, y + 15))

        # Stability
        stab_text = body_font.render(f"Stab{self.get_effective_stability()}", True, (0, 0, 0))
        surface.blit(stab_text, (x + 10, y + height - stab_text.get_height() - 10))

        # Type
        type_text = body_font.render(self.type.value, True, (0, 0, 0))
        type_rect = type_text.get_rect(centerx=x + width//2, y=y + 60)
        surface.blit(type_text, type_rect)

        # Effect (truncated if too long)
        if self.effect:
            effect_lines = self.wrap_text(self.effect, body_font, width - 20)
            for i, line in enumerate(effect_lines[:3]):  # Max 3 lines
                effect_text = body_font.render(line, True, (0, 0, 0))
                surface.blit(effect_text, (x + 10, y + 100 + i * 20))
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def contains_point(self, point):
        """Check if point is within the card's rect"""
        return self.rect and self.rect.collidepoint(point)
    
    def copy(self):
        """Create a copy of this card"""
        return Card(self.name, self.type, self.base_speed, self.base_damage,
                    self.base_stability, self.effect, self.read, self.clash)
