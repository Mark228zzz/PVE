"""
Wave management system.
Controls enemy spawning, wave progression, and difficulty scaling.
"""

import random
from config import (WORLD_WIDTH, WORLD_HEIGHT, WAVE_BASE_ENEMIES,
                    WAVE_ENEMY_INCREMENT, DIFFICULTY_SETTINGS)


class WaveManager:
    """Manages wave progression and enemy spawning"""

    def __init__(self, difficulty='normal'):
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.current_wave = 0
        self.waves_to_win = self.difficulty_settings['waves_to_win']
        self.enemies_remaining = 0
        self.wave_active = False

        # Enemy type progression
        self.available_enemy_types = self._get_available_types()

    def _get_available_types(self):
        """Get enemy types available based on wave progression"""
        # Start with basic enemies, unlock more as waves progress
        return {
            0: ['shooter'],
            3: ['shooter', 'bouncer'],
            6: ['shooter', 'bouncer', 'exploder'],
            10: ['shooter', 'bouncer', 'exploder', 'tank']
        }

    def start_wave(self):
        """Start next wave"""
        self.current_wave += 1
        self.wave_active = True

        # Calculate enemies for this wave
        base_count = WAVE_BASE_ENEMIES + (self.current_wave - 1) * WAVE_ENEMY_INCREMENT
        self.enemies_remaining = int(base_count * self.difficulty_settings['spawn_rate_multiplier'])

        return self._get_wave_info()

    def get_enemy_spawn_list(self):
        """Get list of enemy types to spawn for current wave"""
        if not self.wave_active:
            return []

        # Get available enemy types for current wave
        types = ['shooter']  # Default
        for wave_threshold, enemy_types in sorted(self.available_enemy_types.items()):
            if self.current_wave >= wave_threshold:
                types = enemy_types

        # Create spawn list with weighted randomness
        spawn_list = []
        for _ in range(self.enemies_remaining):
            enemy_type = self._select_enemy_type(types)
            spawn_list.append(enemy_type)

        return spawn_list

    def _select_enemy_type(self, available_types):
        """Select enemy type with weighted randomness"""
        # Weight distribution based on wave number
        weights = {
            'shooter': 10,
            'bouncer': 5 + min(self.current_wave, 10),
            'exploder': 3 + min(self.current_wave // 2, 8),
            'tank': min(self.current_wave // 3, 5)
        }

        # Filter to available types
        type_weights = [(t, weights.get(t, 1)) for t in available_types]
        types, type_weights = zip(*type_weights)

        return random.choices(types, weights=type_weights)[0]

    def enemy_killed(self):
        """Called when an enemy is killed"""
        self.enemies_remaining -= 1
        if self.enemies_remaining <= 0:
            self.wave_active = False

    def is_wave_complete(self):
        """Check if current wave is complete"""
        return not self.wave_active and self.enemies_remaining <= 0

    def is_game_won(self):
        """Check if player has won the game"""
        return self.current_wave >= self.waves_to_win and self.is_wave_complete()

    def _get_wave_info(self):
        """Get info about current wave"""
        return {
            'wave_number': self.current_wave,
            'total_waves': self.waves_to_win,
            'enemies_count': self.enemies_remaining
        }

    def get_spawn_position(self, player_pos, min_distance=300):
        """Get spawn position near world borders, away from player"""
        border_margin = 150  # Distance from edge to spawn

        # Choose which border to spawn on (0=top, 1=right, 2=bottom, 3=left)
        border = random.randint(0, 3)

        max_attempts = 10
        for _ in range(max_attempts):
            if border == 0:  # Top
                x = random.randint(border_margin, WORLD_WIDTH - border_margin)
                y = random.randint(50, border_margin)
            elif border == 1:  # Right
                x = random.randint(WORLD_WIDTH - border_margin, WORLD_WIDTH - 50)
                y = random.randint(border_margin, WORLD_HEIGHT - border_margin)
            elif border == 2:  # Bottom
                x = random.randint(border_margin, WORLD_WIDTH - border_margin)
                y = random.randint(WORLD_HEIGHT - border_margin, WORLD_HEIGHT - 50)
            else:  # Left
                x = random.randint(50, border_margin)
                y = random.randint(border_margin, WORLD_HEIGHT - border_margin)

            distance = ((x - player_pos.x) ** 2 + (y - player_pos.y) ** 2) ** 0.5
            if distance >= min_distance:
                return (x, y)

            # Try next border
            border = (border + 1) % 4

        # Fallback: random border position
        if border == 0:
            return (random.randint(border_margin, WORLD_WIDTH - border_margin), 80)
        elif border == 1:
            return (WORLD_WIDTH - 80, random.randint(border_margin, WORLD_HEIGHT - border_margin))
        elif border == 2:
            return (random.randint(border_margin, WORLD_WIDTH - border_margin), WORLD_HEIGHT - 80)
        else:
            return (80, random.randint(border_margin, WORLD_HEIGHT - border_margin))

    def get_difficulty_multipliers(self):
        """Get difficulty multipliers for enemy creation"""
        return {
            'enemy_speed_multiplier': self.difficulty_settings['enemy_speed_multiplier'],
            'enemy_hp_multiplier': self.difficulty_settings['enemy_hp_multiplier'],
            'enemy_damage_multiplier': self.difficulty_settings['enemy_damage_multiplier']
        }
