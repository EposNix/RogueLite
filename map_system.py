from enum import Enum
import random

class NodeType(Enum):
    COMBAT = "Combat"
    ELITE = "Elite"  
    EVENT = "Event"
    SHOP = "Shop"
    CAMP = "Camp"
    TREASURE = "Treasure"
    BOSS = "Boss"

class MapNode:
    def __init__(self, node_type, floor, choices=None):
        self.type = node_type
        self.floor = floor
        self.completed = False
        self.choices = choices or []  # For events with multiple outcomes
        
    def get_display_name(self):
        """Get user-friendly name for the node"""
        return self.type.value
    
    def get_icon(self):
        """Get simple text icon for mobile display"""
        icons = {
            NodeType.COMBAT: "⚔️",
            NodeType.ELITE: "💀", 
            NodeType.EVENT: "❓",
            NodeType.SHOP: "🏪",
            NodeType.CAMP: "🔥",
            NodeType.TREASURE: "💰",
            NodeType.BOSS: "👑"
        }
        return icons.get(self.type, "?")

class Act:
    def __init__(self, act_number, floors_per_act=10):
        self.act_number = act_number
        self.floors_per_act = floors_per_act
        self.current_floor = 0
        self.nodes = self._generate_act()
    
    def _generate_act(self):
        """Generate a simple act with predetermined structure"""
        nodes = []
        
        # Simple structure for mobile-friendly gameplay:
        # Floors 1-7: Mix of Combat, Event, Shop, Camp, Treasure
        # Floor 8: Elite (forced)
        # Floor 9: Camp (rest before boss)
        # Floor 10: Boss
        
        for floor in range(1, self.floors_per_act + 1):
            if floor == self.floors_per_act - 2:  # Floor 8
                # Elite floor
                nodes.append([MapNode(NodeType.ELITE, floor)])
            elif floor == self.floors_per_act - 1:  # Floor 9  
                # Pre-boss camp
                nodes.append([MapNode(NodeType.CAMP, floor)])
            elif floor == self.floors_per_act:  # Floor 10
                # Boss floor
                nodes.append([MapNode(NodeType.BOSS, floor)])
            else:
                # Regular floors - generate 3 choices
                floor_nodes = self._generate_floor_choices(floor)
                nodes.append(floor_nodes)
        
        return nodes
    
    def _generate_floor_choices(self, floor):
        """Generate 3 node choices for a regular floor"""
        # Weight different node types based on floor and act
        weights = self._get_node_weights(floor)
        
        choices = []
        available_types = list(weights.keys())
        
        # Ensure at least one combat option (core gameplay)
        choices.append(MapNode(NodeType.COMBAT, floor))
        available_types.remove(NodeType.COMBAT)
        
        # Add 2 more varied choices
        for _ in range(2):
            if available_types:
                node_type = random.choices(
                    available_types, 
                    weights=[weights[t] for t in available_types]
                )[0]
                choices.append(MapNode(node_type, floor))
                # Remove to avoid duplicates in same floor
                available_types.remove(node_type)
        
        # If we need more choices and ran out of types, add more combat
        while len(choices) < 3:
            choices.append(MapNode(NodeType.COMBAT, floor))
        
        return choices
    
    def _get_node_weights(self, floor):
        """Get weighted probabilities for different node types"""
        base_weights = {
            NodeType.COMBAT: 40,
            NodeType.EVENT: 25, 
            NodeType.SHOP: 15,
            NodeType.CAMP: 10,
            NodeType.TREASURE: 10
        }
        
        # Adjust weights based on floor position
        if floor <= 3:  # Early floors
            base_weights[NodeType.COMBAT] = 50  # More combat early
            base_weights[NodeType.SHOP] = 20    # More shops early
        elif floor >= 6:  # Later floors  
            base_weights[NodeType.EVENT] = 30   # More events later
            base_weights[NodeType.CAMP] = 15    # More camps later
        
        return base_weights
    
    def get_current_choices(self):
        """Get the 3 choices for the current floor"""
        if self.current_floor < len(self.nodes):
            return self.nodes[self.current_floor]
        return []
    
    def advance_floor(self, chosen_node):
        """Advance to next floor after completing chosen node"""
        chosen_node.completed = True
        self.current_floor += 1
        return self.current_floor < len(self.nodes)  # Returns True if more floors exist

class MapSystem:
    def __init__(self):
        self.current_act = 1
        self.acts = {}
        self.player_path = []  # Track which nodes player chose
        self.gold = 100  # Starting currency
        
        # Initialize all acts
        for act_num in range(1, 4):  # 3 acts total
            self.acts[act_num] = Act(act_num)
    
    def get_current_act(self):
        """Get the current act"""
        return self.acts.get(self.current_act)
    
    def get_current_choices(self):
        """Get the 3 node choices for current position"""
        current_act = self.get_current_act()
        if current_act:
            return current_act.get_current_choices()
        return []
    
    def choose_node(self, node_index):
        """Player chooses one of the 3 available nodes"""
        choices = self.get_current_choices()
        if 0 <= node_index < len(choices):
            chosen_node = choices[node_index]
            self.player_path.append(chosen_node)
            
            # Advance the current act
            current_act = self.get_current_act()
            has_more_floors = current_act.advance_floor(chosen_node)
            
            # Check if act is complete
            if not has_more_floors:
                self.current_act += 1
                if self.current_act > 3:
                    return None  # Run complete
            
            return chosen_node
        return None
    
    def is_run_complete(self):
        """Check if the entire run is finished"""
        return self.current_act > 3
    
    def get_act_progress(self):
        """Get current act and floor for UI display"""
        current_act = self.get_current_act()
        if current_act:
            return (self.current_act, current_act.current_floor + 1, current_act.floors_per_act)
        return (4, 1, 1)  # Run complete
    
    def get_rewards_for_node(self, node):
        """Get rewards for completing a node (placeholder)"""
        rewards = {
            "gold": 0,
            "card_choices": 0,
            "relic": False,
            "heal": 0
        }
        
        if node.type == NodeType.COMBAT:
            rewards["gold"] = random.randint(10, 18)
            rewards["card_choices"] = 1
        elif node.type == NodeType.ELITE:
            rewards["gold"] = random.randint(25, 35) 
            rewards["card_choices"] = 1
            rewards["relic"] = True
        elif node.type == NodeType.BOSS:
            rewards["gold"] = random.randint(40, 60)
            rewards["card_choices"] = 1
            rewards["relic"] = True
        elif node.type == NodeType.TREASURE:
            rewards["gold"] = random.randint(20, 30)
            rewards["relic"] = True
        elif node.type == NodeType.CAMP:
            rewards["heal"] = 25  # Percentage heal
        
        return rewards