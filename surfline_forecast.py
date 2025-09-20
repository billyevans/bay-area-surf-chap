#!/usr/bin/env python3
"""
Surfline Forecast Fetcher with Board Recommendations
Similar to https://github.com/mhelmetag/surflinef but with board analysis
"""

import requests
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Optional
import sys

class SurflineAPI:
    """Handle Surfline API requests"""

    BASE_URL = "https://services.surfline.com/kbyg/spots/forecasts"
    DEFAULT_SPOTS_FILE = "surf_spots.json"

    def __init__(self):
        self.session = requests.Session()
        # Surfline requires these headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Load surf spots from file
        self.spots = self._load_surf_spots()

    def _load_surf_spots(self) -> Dict[str, Dict]:
        """Load surf spots from JSON file"""
        try:
            with open(self.DEFAULT_SPOTS_FILE, 'r') as f:
                spots_list = json.load(f)

            # Convert list to dict for easy lookup by name
            spots_dict = {}
            for spot in spots_list:
                # Create lookup by name (normalized)
                normalized_name = spot['name'].lower().replace(" ", "_").replace("-", "_")
                spots_dict[normalized_name] = spot

                # Also add direct name lookup
                spots_dict[spot['name'].lower()] = spot

            print(f"✅ Loaded {len(spots_list)} surf spots from {self.DEFAULT_SPOTS_FILE}")
            return spots_dict

        except FileNotFoundError:
            print(f"❌ Spots file not found: {self.DEFAULT_SPOTS_FILE}")
            print(f"💡 Please create {self.DEFAULT_SPOTS_FILE} with surf spot configurations")
            sys.exit(1)

    def get_spot_info(self, spot_name: str) -> Optional[Dict]:
        """Get complete spot information including characteristics"""
        normalized_name = spot_name.lower().replace(" ", "_").replace("-", "_")
        spot_info = self.spots.get(normalized_name) or self.spots.get(spot_name.lower())

        if spot_info:
            return spot_info

        # If not found, show available spots
        available_spots = [spot['name'] for spot in self.spots.values() if 'name' in spot]
        unique_spots = list(set(available_spots))  # Remove duplicates
        print(f"❌ Spot '{spot_name}' not found. Available spots: {', '.join(unique_spots[:10])}")
        return None

    def get_spot_id(self, spot_name: str) -> Optional[str]:
        """Get Surfline spot ID from name"""
        spot_info = self.get_spot_info(spot_name)
        return spot_info['surfline_id'] if spot_info else None

    def fetch_forecast(self, spot_id: str, days: int = 1) -> Optional[Dict]:
        """Fetch wave forecast data"""
        try:
            url = f"{self.BASE_URL}/wave"
            params = {
                'spotId': spot_id,
                'days': days,
                'intervalHours': 1
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error fetching wave data: {e}")
            return None

    def fetch_wind(self, spot_id: str, days: int = 1) -> Optional[Dict]:
        """Fetch wind forecast data"""
        try:
            url = f"{self.BASE_URL}/wind"
            params = {
                'spotId': spot_id,
                'days': days,
                'intervalHours': 1
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error fetching wind data: {e}")
            return None

    def fetch_tides(self, spot_id: str, days: int = 1) -> Optional[Dict]:
        """Fetch tide data"""
        try:
            url = f"{self.BASE_URL}/tides"
            params = {
                'spotId': spot_id,
                'days': days
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error fetching tide data: {e}")
            return None

class BoardQuiver:
    """Manage surfboard collection and recommendations"""

    DEFAULT_BOARDS_FILE = "my_boards.json"
    DEFAULT_CONSTRUCTIONS_FILE = "board_constructions.json"

    def __init__(self, boards_file: str = None, constructions_file: str = None):
        """Load boards and constructions from JSON files"""

        # Load constructions first
        self.construction_properties = self._load_constructions(constructions_file)

        # Load boards
        boards_to_load = boards_file or self.DEFAULT_BOARDS_FILE
        try:
            with open(boards_to_load, 'r') as f:
                self.boards = json.load(f)
            print(f"✅ Loaded {len(self.boards)} boards from {boards_to_load}")
        except FileNotFoundError:
            print(f"❌ Boards file not found: {boards_to_load}")
            print(f"💡 Please create {boards_to_load} with your board specifications")
            print("📖 See README.md for configuration examples")
            sys.exit(1)

    def _load_constructions(self, constructions_file: str = None) -> Dict:
        """Load construction properties from JSON file"""
        file_to_load = constructions_file or self.DEFAULT_CONSTRUCTIONS_FILE

        try:
            with open(file_to_load, 'r') as f:
                constructions = json.load(f)
            print(f"✅ Loaded {len(constructions)} construction types from {file_to_load}")
            return constructions
        except FileNotFoundError:
            print(f"❌ Constructions file not found: {file_to_load}")
            print(f"💡 Please create {file_to_load} with construction specifications")
            # Return minimal default to prevent complete failure
            return {
                "pu": {
                    "full_name": "Polyurethane/Polyester",
                    "durability": "medium",
                    "flex": "high",
                    "paddle_power": "medium",
                    "small_wave_performance": "good",
                    "powerful_wave_performance": "excellent",
                    "description": "Traditional polyurethane foam with polyester resin."
                }
            }

    def recommend_board(self, wave_height: float, period: float, wind_speed: float, spot_info: Dict = None) -> List[Dict]:
        """Recommend best board based on conditions with construction and spot considerations"""
        scores = []

        for board in self.boards:
            score = 0
            reasoning = []
            # Default to PU construction if not specified
            construction_type = board.get("construction", "pu")
            construction = self.construction_properties.get(construction_type, self.construction_properties.get("pu", {}))

            # Wave height scoring
            min_wave, max_wave = board["ideal_wave_range"]
            if min_wave <= wave_height <= max_wave:
                score += 3
                reasoning.append(f"Perfect wave size ({wave_height}ft in {min_wave}-{max_wave}ft range)")
            elif wave_height < min_wave:
                score += max(0, 2 - (min_wave - wave_height))
                reasoning.append(f"Below ideal size ({wave_height}ft vs {min_wave}ft+ ideal)")
            else:
                score += max(0, 2 - (wave_height - max_wave))
                reasoning.append(f"Above ideal size ({wave_height}ft vs {max_wave}ft max)")

            # Period scoring
            min_period, max_period = board["ideal_period_range"]
            if min_period <= period <= max_period:
                score += 2
                reasoning.append(f"Good period ({period}s in {min_period}-{max_period}s range)")
            else:
                score += max(0, 1 - abs(period - (min_period + max_period) / 2) / 5)
                reasoning.append(f"Period okay ({period}s vs {min_period}-{max_period}s ideal)")

            # Wind scoring (lower is better)
            if wind_speed < 10:
                score += 1
                reasoning.append("Clean conditions")
            elif wind_speed < 15:
                score += 0.5
                reasoning.append("Slightly windy")
            else:
                reasoning.append("Windy conditions")

            # Spot-specific scoring
            if spot_info and 'characteristics' in spot_info:
                characteristics = spot_info['characteristics']
                spot_type = spot_info.get('type', 'unknown')

                # Beach break bonuses
                if spot_type == "beach_break":
                    if board["type"] in ["fish/hybrid", "longboard"]:
                        score += 0.5
                        reasoning.append("Great for beach breaks")

                # Reef/point break bonuses
                elif spot_type in ["reef_break", "point_break"]:
                    if board["type"] == "performance_shortboard" and period > 12:
                        score += 1
                        reasoning.append("Performance board ideal for reef breaks")
                    elif board["type"] == "gun" and wave_height > 6:
                        score += 1.5
                        reasoning.append("Gun perfect for big reef waves")

                # Wave quality considerations
                wave_quality = characteristics.get('wave_quality', 'unknown')
                if wave_quality == "forgiving" and board["type"] in ["fish/hybrid", "longboard"]:
                    score += 0.5
                    reasoning.append("Forgiving waves suit this board type")
                elif wave_quality in ["excellent", "challenging"] and board["type"] == "performance_shortboard":
                    score += 0.5
                    reasoning.append("High-performance board for quality waves")

                # Skill level matching
                skill_level = characteristics.get('skill_level', 'unknown')
                if skill_level == "beginner_friendly" and board["volume"] > 35:
                    score += 0.5
                    reasoning.append("Extra volume good for forgiving spots")
                elif skill_level == "advanced" and board["volume"] < 35:
                    score += 0.5
                    reasoning.append("Lower volume suits advanced breaks")

            # Construction-based bonuses
            if construction:
                # Small wave construction bonuses
                if wave_height < 3 and construction.get("small_wave_performance") == "excellent":
                    score += 1
                    reasoning.append(f"{construction_type} construction excels in small waves")

                # Powerful wave construction bonuses
                if period > 13 and construction.get("powerful_wave_performance") == "excellent":
                    score += 1
                    reasoning.append(f"{construction_type} construction handles power well")

                # Paddle power in weak conditions
                if wave_height < 3 and period < 10 and construction.get("paddle_power") in ["high", "excellent"]:
                    score += 0.5
                    reasoning.append(f"{construction_type} gives extra paddle power")

                # Responsiveness in quality waves
                if period > 12 and construction.get("flex") in ["high", "medium-high"]:
                    score += 0.5
                    reasoning.append(f"{construction_type} provides responsive feel")

            # Board type specific bonuses
            if board["type"] == "fish/hybrid" and wave_height < 3:
                score += 1
                reasoning.append("Fish design excels in small waves")
            elif board["type"] == "performance_shortboard" and period > 12:
                score += 1
                reasoning.append("Performance board great for powerful waves")
            elif board["type"] == "twin_fin" and 3 <= wave_height <= 5:
                score += 0.5
                reasoning.append("Twin fin sweet spot conditions")

            scores.append({
                "board": board,
                "construction_info": construction,
                "construction_type": construction_type,
                "score": score,
                "reasoning": reasoning
            })

        # Sort by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

class SurflineForecast:
    """Main application class"""

    def __init__(self):
        self.api = SurflineAPI()
        self.quiver = BoardQuiver()

    def parse_conditions(self, wave_data: Dict, wind_data: Dict, tide_data: Dict) -> Dict:
        """Parse current conditions from API responses"""
        try:
            # Get current wave conditions (first data point)
            current_wave = wave_data['data']['wave'][0]
            wave_height = (current_wave['surf']['min'] + current_wave['surf']['max']) / 2
            period = current_wave.get('swells', [{}])[0].get('period', 0)

            # Get current wind
            current_wind = wind_data['data']['wind'][0] if wind_data else {}
            wind_speed = current_wind.get('speed', 0)
            wind_direction = current_wind.get('direction', 0)

            # Get tide info
            tide_info = "N/A"
            if tide_data and 'data' in tide_data:
                tide_info = "Available"

            return {
                "wave_height": wave_height,
                "period": period,
                "wind_speed": wind_speed,
                "wind_direction": wind_direction,
                "tide": tide_info,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing conditions: {e}")
            return None

    def format_output(self, spot_name: str, spot_info: Dict, conditions: Dict, recommendations: List[Dict]) -> str:
        """Format output for display with construction and spot details"""
        spot_type = spot_info.get('type', 'unknown').replace('_', ' ').title() if spot_info else 'Unknown'
        spot_description = spot_info.get('description', '') if spot_info else ''

        output = f"""
🏄‍♂️ SURF FORECAST: {spot_name.upper()}
{'='*60}
📍 SPOT INFO:
   Type: {spot_type}
   {spot_description}

📊 CONDITIONS:
   Wave Height: {conditions['wave_height']:.1f}ft
   Period: {conditions['period']:.0f}s
   Wind: {conditions['wind_speed']:.0f}mph @ {conditions['wind_direction']:.0f}°
   Updated: {datetime.fromisoformat(conditions['timestamp'].replace('Z', '+00:00')).strftime('%H:%M %Z')}

🏄‍♂️ BOARD RECOMMENDATIONS:
"""

        for i, rec in enumerate(recommendations[:3], 1):
            board = rec['board']
            construction_info = rec.get('construction_info', {})
            construction_type = rec.get('construction_type', 'pu')
            # Always display width, use 'N/A' if not specified
            width = board.get('width', 'N/A')
            output += f"""
{i}. {board['name']} (Score: {rec['score']:.1f}/8.0)
   📏 {board['length']} x {width} | 💧 {board['volume']}L | 🏄‍♂️ {board['type']}
   🔧 {construction_type.title()} Construction
   💡 {construction_info.get('description', 'Traditional polyurethane construction')}
   💭 {board['description']}
   ✓ {' | '.join(rec['reasoning'])}
"""

        # Add spot-specific analysis for top recommendation
        if recommendations and spot_info:
            top_board = recommendations[0]
            characteristics = spot_info.get('characteristics', {})
            output += f"""
📍 SPOT ANALYSIS (Top Pick):
   Wave Quality: {characteristics.get('wave_quality', 'unknown').title()}
   Skill Level: {characteristics.get('skill_level', 'unknown').replace('_', ' ').title()}
   Crowd Factor: {characteristics.get('crowd_factor', 'unknown').title()}
   Best Boards for This Spot: {', '.join(characteristics.get('best_boards', []))}
"""

        output += f"""
{'='*60}
🤙 RECOMMENDATION SUMMARY:
{spot_name} ({spot_type}): {conditions['wave_height']:.1f}ft @ {conditions['period']:.0f}s, {conditions['wind_speed']:.0f}mph wind
→ Take the {recommendations[0]['board']['name']} ({recommendations[0].get('construction_type', 'pu')} construction)
"""

        return output

    def run(self, spot_name: str, save_json: bool = False) -> str:
        """Main execution function"""

        # Get spot information
        spot_info = self.api.get_spot_info(spot_name)
        if not spot_info:
            return f"❌ Unknown spot '{spot_name}'. Check available spots with --list-spots"

        spot_id = spot_info['surfline_id']
        print(f"🌊 Fetching forecast for {spot_name} ({spot_info.get('type', 'unknown').replace('_', ' ')})...")

        # Fetch data
        wave_data = self.api.fetch_forecast(spot_id)
        wind_data = self.api.fetch_wind(spot_id)
        tide_data = self.api.fetch_tides(spot_id)

        if not wave_data:
            return "❌ Failed to fetch wave data"

        # Parse conditions
        conditions = self.parse_conditions(wave_data, wind_data, tide_data)
        if not conditions:
            return "❌ Failed to parse conditions"

        # Get board recommendations with spot consideration
        recommendations = self.quiver.recommend_board(
            conditions['wave_height'],
            conditions['period'],
            conditions['wind_speed'],
            spot_info  # Pass spot info for spot-specific scoring
        )

        # Save raw data if requested
        if save_json:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"surfline_{spot_name}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'spot_info': spot_info,
                    'conditions': conditions,
                    'recommendations': recommendations,
                    'raw_data': {
                        'wave': wave_data,
                        'wind': wind_data,
                        'tide': tide_data
                    }
                }, f, indent=2)
            print(f"💾 Raw data saved to {filename}")

        return self.format_output(spot_name, spot_info, conditions, recommendations)

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Surfline forecast fetcher with board recommendations')
    parser.add_argument('spot', nargs='?', default='linda_mar',
                       help='Surf spot name (default: linda_mar)')
    parser.add_argument('--save-json', action='store_true',
                       help='Save raw JSON data to file')
    parser.add_argument('--list-spots', action='store_true',
                       help='List available surf spots')

    args = parser.parse_args()

    forecast = SurflineForecast()

    if args.list_spots:
        print("Available surf spots:")
        api = SurflineAPI()
        # Get unique spot names from the loaded spots
        unique_spots = []
        for spot_info in api.spots.values():
            if isinstance(spot_info, dict) and 'name' in spot_info:
                if spot_info['name'] not in unique_spots:
                    unique_spots.append(spot_info['name'])

        for spot in sorted(unique_spots):
            spot_info = api.get_spot_info(spot)
            spot_type = spot_info.get('type', 'unknown').replace('_', ' ').title() if spot_info else 'Unknown'
            print(f"  - {spot} ({spot_type})")
        return

    try:
        result = forecast.run(args.spot, args.save_json)
        print(result)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
