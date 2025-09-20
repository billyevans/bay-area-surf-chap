# 🏄‍♂️ Bay Area Surf Chap

> Your friendly Bay Area surf advisor - because choosing the right board shouldn't be guesswork!

Bay Area Surf Chap fetches real-time surf conditions from Surfline and recommends the perfect board from your quiver. It considers wave height, period, wind conditions, spot characteristics, and even your board's construction to give you spot-on recommendations.

## ✨ Features

- **Real-time Surfline Data** - Fetches current wave, wind, and tide conditions
- **Smart Board Recommendations** - Analyzes your quiver against conditions
- **Spot-Specific Analysis** - Knows the difference between Linda Mar and Pleasure Point
- **Construction Awareness** - Factors in Libtech vs PU vs EPS performance characteristics
- **11 Bay Area Spots** - From Linda Mar to Davenport to The Hook
- **Customizable Quiver** - Easy JSON configuration for your boards
- **Standalone Tool** - Complete surf analysis and recommendations

## 🏄‍♂️ Supported Surf Spots

- **Linda Mar** - Beginner-friendly beach break
- **Linda Mar North** - Less crowded northern section
- **Rockaway** - Challenging cove with powerful rights
- **Montara** - Advanced beach break with barrels
- **Princeton Jetty** - Protected jetty break
- **Davenport** - World-class reef break (experts only)
- **Waddell Creek** - Consistent beach break
- **Fort Point** - Iconic SF break under Golden Gate
- **Pleasure Point** - Famous Santa Cruz point break
- **The Hook** - Mellow point break
- **South Ocean Beach** - Heavy, powerful beach break

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/bay-area-surf-chap.git
cd bay-area-surf-chap
pip install requests
```

### Setup Your Board Quiver

**Required**: Create `my_boards.json` with your actual surfboards:

```bash
# Copy the example and customize with your boards
cp my_boards_example.json my_boards.json
# Edit with your actual board specifications
```

Or create from scratch:

```json
[
  {
    "name": "Your Board Name",
    "length": "5'9\"",
    "width": "21\"",
    "volume": 35.25,
    "type": "fish/hybrid",
    "construction": "libtech",
    "ideal_wave_range": [2, 5],
    "ideal_period_range": [8, 13],
    "description": "Your go-to small wave board"
  }
]
```

### Basic Usage

```bash
# Get recommendations for Linda Mar
python surfline_forecast.py "Linda Mar"

# Check out Pleasure Point
python surfline_forecast.py "Pleasure Point"

# List all available spots
python surfline_forecast.py --list-spots

# Save raw data for analysis
python surfline_forecast.py "Princeton Jetty" --save-json
```

### Sample Output

```
🏄‍♂️ SURF FORECAST: LINDA MAR
============================================================
📍 SPOT INFO:
   Type: Beach Break
   Forgiving beach break perfect for beginners. Protected valley location.

📊 CONDITIONS:
   Wave Height: 4.5ft
   Period: 11s
   Wind: 6mph @ 280°

🏄‍♂️ BOARD RECOMMENDATIONS:
1. Libtech RNF96 (Score: 6.2/8.0)
   📏 5'9" x 21" | 💧 35.25L | 🏄‍♂️ fish/hybrid
   🔧 Libtech Construction
   💡 Bomb-proof construction, great paddle power
   ✓ Perfect wave size | Great for beach breaks | Libtech excels in small waves

🤙 RECOMMENDATION SUMMARY:
Linda Mar (Beach Break): 4.5ft @ 11s, 6mph wind
→ Take the Libtech RNF96 (libtech construction)
```

## ⚙️ Configuration

### Your Board Quiver

Edit `my_boards.json` to match your actual surfboards:

```json
[
  {
    "name": "Your Board Name",
    "length": "5'9\"",
    "width": "21\"",
    "volume": 35.25,
    "type": "fish/hybrid",
    "construction": "libtech",
    "ideal_wave_range": [2, 5],
    "ideal_period_range": [8, 13],
    "description": "Your go-to small wave board"
  }
]
```

### Construction Types

Bay Area Surf Chap includes detailed construction analysis. Edit `board_constructions.json` to add or modify construction types:

```json
{
  "your_construction": {
    "full_name": "Your Construction Name",
    "durability": "high",
    "flex": "medium",
    "paddle_power": "high",
    "small_wave_performance": "excellent",
    "powerful_wave_performance": "good",
    "description": "Description of construction characteristics"
  }
}
```

### Supported Board Types
- `fish/hybrid` - Small wave specialists
- `performance_shortboard` - All-around performance
- `twin_fin` - Playful, skatey feel
- `gun` - Big wave boards
- `step_up` - Powerful wave boards

### Included Construction Types
- **`pu`** - Traditional polyurethane, responsive feel
- **`eps`** - Lightweight EPS/epoxy, great paddle power
- **`libtech`** - Bomb-proof Lib Tech construction
- **`fused_cell_eps`** - EPS core with PU rails (Aipa style)
- **`xtr_parallel_carbon`** - Carbon fiber reinforcement
- **`darkarts`** - Revolutionary carbon fiber vacuum-bagged construction
- **`carbon_kevlar`** - Hybrid carbon-kevlar weave
- **`tuflite`** - Molded Surftech construction

## 🎯 How It Works

1. **Fetches Real Data** - Connects to Surfline's API for current conditions
2. **Analyzes Your Quiver** - Scores each board against wave conditions
3. **Considers Spot Characteristics** - Beach breaks favor different boards than reef breaks
4. **Factors Construction** - Libtech boards get bonuses in small waves, PU in powerful waves
5. **Provides Recommendations** - Ranked list with detailed reasoning

## 🔧 Advanced Usage

### Custom Spots File

The `surf_spots.json` file contains detailed information about each surf spot. You can add new spots or modify existing ones:

```json
{
  "name": "Your Local Break",
  "surfline_id": "your_surfline_id_here",
  "type": "reef_break",
  "characteristics": {
    "wave_quality": "excellent",
    "skill_level": "advanced",
    "best_boards": ["shortboard", "gun"]
  }
}
```

### Integration as a Standalone Tool

Bay Area Surf Chap provides complete surf analysis and board recommendations in one place:

1. Set up your board quiver in `my_boards.json`
2. Run the script for any Bay Area spot
3. Get detailed conditions and board analysis
4. Make informed decisions about your surf session
5. Track conditions over time with the `--save-json` option

**Note**: The script will create default configuration files for constructions and surf spots automatically, but you must create your own board quiver file.

## 📊 Scoring Algorithm

Boards are scored on multiple factors:

- **Wave Size Match** (0-3 points) - How well the board handles current wave height
- **Period Compatibility** (0-2 points) - Board performance in current swell period
- **Wind Conditions** (0-1 points) - Clean vs windy condition bonuses
- **Spot-Specific Bonuses** (0-1.5 points) - Beach break vs reef break preferences
- **Construction Bonuses** (0-1 points) - Construction performance in conditions

Maximum score: 8.0 points
