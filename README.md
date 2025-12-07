# PVE Arena Game

A challenging wave-based survival shooter with multiple enemy types, powerful abilities, and progressive difficulty scaling.

## Features

### Menu System
- **Main Menu**: Start Game, Settings, Quit
- **Settings Menu**: Toggle grid display and health bars
- **Difficulty Selection**: Choose Easy, Normal, or Hard when starting a game
- **Pause System**: Press ESC anytime to pause
- **Victory/Game Over Screens**: Complete feedback with stats

### Game Modes
- **3 Difficulty Levels**: Easy (10 waves), Normal (15 waves), Hard (20 waves)
- **Progressive Wave System**: More enemies each wave with increasing difficulty
- **Wave Transitions**: 10-second countdown between waves
- **Win Condition**: Survive all waves to victory

### Enemy Types

1. **Shooter** (Red Circle)
   - Shoots projectiles from a distance
   - Follows player but maintains safe distance
   - Standard difficulty

2. **Exploder** (Orange Circle)
   - Rushes the player
   - Explodes on contact dealing area damage
   - Fast and dangerous up close

3. **Bouncer** (Green Triangle)
   - Bounces around the arena randomly
   - Deals damage on collision
   - Unpredictable movement

4. **Tank** (Blue Square)
   - High HP, slow movement
   - Powerful shots
   - Difficult to kill

### Player Abilities
The player has 3 powerful mana-based abilities:

1. **Dash (Q)** - Costs 15 mana
   - Instantly dash forward 200 units in facing direction
   - 3 second cooldown
   - Great for dodging or repositioning

2. **Shield (E)** - Costs 25 mana
   - Become invincible for 5 seconds
   - Visual pulsing shield effect
   - 15 second cooldown

3. **Burst (R)** - Costs 20 mana
   - Area damage explosion (150 radius)
   - Deals 15 damage to all enemies in range
   - 8 second cooldown

### Upgrade System
Spend mana to permanently upgrade your stats:
- **Damage (1)**: Increase bullet damage (+5 per level)
- **Speed (2)**: Increase bullet speed (+50 per level)
- **Max HP (3)**: Increase max health (+20) and heal (+30)

Upgrade costs increase with each level: Base cost + 5-7 mana per level

### Controls
- **WASD**: Move player
- **Mouse Click**: Shoot
- **Q**: Dash ability
- **E**: Shield ability
- **R**: Burst ability
- **1, 2, 3**: Upgrade Damage/Speed/HP
- **ESC**: Pause/Resume

### Visual Effects
- **Particle System**: Enemies explode into colorful particles when defeated
- **Shield Animation**: Pulsing visual effect during invincibility
- **Smooth Camera**: Follows player movement across the world
- **Modern UI**: Semi-transparent panels with smooth animations

## Code Architecture

### Adding New Enemy Types

The game is designed for easy expansion. To add a new enemy:

1. **Add configuration** in `config.py`:
```python
ENEMY_TYPES = {
    'your_enemy': {
        'color': (R, G, B),
        'min_radius': 10,
        'max_radius': 15,
        'hp': 30,
        # ... other stats
        'shape': 'circle'  # or 'square', 'triangle'
    }
}
```

2. **Create enemy class** in `enemy_types.py`:
```python
class YourEnemy(BaseEnemy):
    def __init__(self, x, y, difficulty_multipliers):
        super().__init__(x, y, 'your_enemy', difficulty_multipliers)
        # Custom initialization

    def update(self, dt, player_pos=None):
        # Custom behavior
        super().update(dt)
```

3. **Register in factory** in `enemy_types.py`:
```python
def create_enemy(enemy_type, x, y, difficulty_multipliers):
    enemy_classes = {
        'your_enemy': YourEnemy,
        # ... existing types
    }
    # ...
```

4. **Add to wave progression** in `wave_manager.py`:
```python
self.available_enemy_types = {
    15: ['shooter', 'bouncer', 'exploder', 'tank', 'your_enemy']
}
```

### Adding Player Abilities

To add new mana-based abilities:

1. **Add constants** in `config.py`:
```python
ABILITY_YOUR_COST = 20
ABILITY_YOUR_COOLDOWN = 5.0
ABILITY_YOUR_EFFECT = 100
```

2. **Add cooldown tracking** in `player.py` `__init__`:
```python
self.your_ability_cooldown = 0
```

3. **Create ability method** in `player.py`:
```python
def use_your_ability(self):
    if self.mana >= ABILITY_YOUR_COST and self.your_ability_cooldown <= 0:
        self.mana -= ABILITY_YOUR_COST
        self.your_ability_cooldown = ABILITY_YOUR_COOLDOWN
        # Ability logic here
        return True
    return False
```

4. **Update cooldown** in `player.py` `update()`:
```python
if self.your_ability_cooldown > 0:
    self.your_ability_cooldown -= dt
```

5. **Add keybinding** in `game.py` `_handle_playing_event`:
```python
elif event.key == pygame.K_f:
    self.player.use_your_ability()
```

### File Structure

```
config.py          - All game configuration and constants
entity.py          - Base entity class with physics
player.py          - Player class with shooting, abilities, and upgrades
enemy_types.py     - All enemy types (Shooter, Bouncer, Exploder, Tank)
bullet.py          - Bullet projectiles for player and enemies
mana.py            - Mana drops from enemies with collection animation
wave_manager.py    - Wave progression, enemy spawning, and border positioning
menu.py            - All menu screens (main, settings, difficulty, pause, victory, game over)
game.py            - Main game loop and state management
camera.py          - Smooth camera following system
particles.py       - Particle system for visual effects
main.py            - Entry point
```

### Game States

The game uses a state machine pattern:
- `MAIN_MENU` - Main menu screen
- `SETTINGS` - Settings configuration
- `DIFFICULTY` - Difficulty selection when starting game
- `PLAYING` - Active gameplay
- `PAUSED` - Game paused
- `VICTORY` - Won the game
- `GAME_OVER` - Player died

## Difficulty Scaling

Each difficulty affects:
- **Player Starting HP**: 60 (easy), 50 (normal), 35 (hard)
- **Enemy Speed**: 0.8x (easy) to 1.4x (hard)
- **Enemy HP**: 0.9x (easy) to 1.6x (hard)
- **Enemy Damage**: 0.8x (easy) to 1.7x (hard)
- **Spawn Rate**: 0.9x (easy) to 1.4x (hard)
- **Waves to Win**: 10 (easy), 15 (normal), 20 (hard)

## Wave Progression

- Waves start with 5 enemies
- Each wave adds 3 more enemies
- 10-second countdown between waves (game paused)
- Enemies spawn near world borders, away from player
- Enemy types unlock progressively:
  - Wave 1+: Shooters
  - Wave 3+: Shooters, Bouncers
  - Wave 6+: Shooters, Bouncers, Exploders
  - Wave 10+: All types including Tanks

## Configuration

All game balance can be tweaked in `config.py`:
- **Screen**: Fullscreen mode, world dimensions (2400x1600)
- **Player Stats**: HP per difficulty, speed, acceleration, friction, turn speed
- **Player Combat**: Bullet speed/damage, shoot delay
- **Player Abilities**: Costs, cooldowns, effects for Dash/Shield/Burst
- **Enemy Configurations**: Stats for all 4 enemy types
- **Difficulty Multipliers**: Speed, HP, damage, spawn rate per difficulty
- **Wave System**: Base enemies, increment per wave
- **Upgrade System**: Base costs, cost increases, stat increases
- **Mana System**: Drop amounts, collection radius/speed

## Requirements

```bash
pip install pygame-ce
```

## Running the Game

```bash
python main.py
```

## Extending the Game

### Ideas for New Features

1. **New Enemy Behaviors**:
   - Healer enemy that restores other enemies' HP
   - Splitter that divides into smaller enemies when killed
   - Shield enemy that blocks bullets
   - Teleporter that blinks around the arena

2. **New Player Abilities** (already implemented: Dash, Shield, Burst):
   - Slow-time field
   - Turret deployment
   - Multi-shot mode
   - Laser beam

3. **Powerups**:
   - Temporary double damage
   - Speed boost
   - Instant cooldown reset
   - Magnetize all mana

4. **Game Modes**:
   - Endless mode (infinite waves)
   - Time attack (kill enemies quickly)
   - Boss battles every 5 waves
   - Co-op multiplayer

All of these can be added by following the patterns established in the existing code!
