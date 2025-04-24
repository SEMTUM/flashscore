import json
import logging
from datetime import datetime
from time import sleep
from typing import List, Dict, Optional, Tuple
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('__main__')

# Constants
API_HEADERS = {"x-fsign": "SW9D1eZo"}
MAX_RETRIES = 3
RETRY_DELAY = 10
MIN_GAMES_THRESHOLD = 5

# API endpoints
BASE_FLASHSCORE_URL = "https://d.flashscorekz.com/x/feed"
BASE_ODDS_URL = "https://global.ds.lsapp.eu/odds/pq_graphql"
BASE_STATS_URL = "https://46.flashscore.ninja/46/x/feed"


class FlashScore:
    """Class for interacting with FlashScore API to get sports data."""

    @staticmethod
    def make_request(url: str) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: URL to make request to
            
        Returns:
            Response object
            
        Raises:
            Exception: After maximum retries exceeded
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url=url, headers=API_HEADERS)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed for URL {url}: {str(e)}")
                logger.info(f"Waiting {RETRY_DELAY} seconds before retry...")
                sleep(RETRY_DELAY)

    @staticmethod
    def parse_match_data(raw_data: str) -> List[Dict]:
        """
        Parse raw match data from FlashScore API.
        
        Args:
            raw_data: Raw response text from API
            
        Returns:
            List of parsed match dictionaries
        """
        data = raw_data.split('¬')
        data_list = [{}]

        for item in data:
            key = item.split('÷')[0]
            value = item.split('÷')[-1]

            if '~' in key:
                data_list.append({key: value})
            else:
                data_list[-1].update({key: value})

        return data_list

    @staticmethod
    def get_matches(sport_id: int, day_offset: int) -> List[Tuple[str, str, str, datetime, str]]:
        """
        Get matches for specified sport and day.
        
        Args:
            sport_id: Sport identifier (3 for basketball)
            day_offset: Day offset (0 - today, -1 - yesterday, 1 - tomorrow)
            
        Returns:
            List of match tuples (id, team1, team2, date, league)
        """
        feed = f'f_{sport_id}_{day_offset}_3_ru_5'
        url = f'{BASE_FLASHSCORE_URL}/{feed}'
        
        try:
            response = FlashScore.make_request(url)
            data_list = FlashScore.parse_match_data(response.text)
        except Exception as e:
            logger.error(f"Failed to get matches: {str(e)}")
            return []

        matches = []
        current_league = "Unknown"
        
        for game in data_list:
            if not game:
                continue
                
            keys = list(game.keys())
            
            if '~ZA' in keys:
                current_league = game.get("~ZA")
                
            if '~AA' in keys:
                try:
                    date = datetime.fromtimestamp(int(game.get("AD")))
                    matches.append((
                        game.get("~AA"),
                        game.get("AE"),
                        game.get("AF"),
                        date,
                        current_league
                    ))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse match data: {str(e)}")

        logger.info(f"Successfully retrieved {len(matches)} matches")
        return matches

    @staticmethod
    def get_odds(match_id: str) -> Optional[Tuple[float, float]]:
        """
        Get odds for a specific match.
        
        Args:
            match_id: Match identifier
            
        Returns:
            Tuple of (odds1, odds2) or None if not available
        """
        url = f'{BASE_ODDS_URL}?_hash=ope&eventId={match_id}&projectId=46&geoIpCode=RU&geoIpSubdivisionCode=RU'
        
        try:
            response = FlashScore.make_request(url)
            data = json.loads(response.text)
            odds = data['data']['findPrematchOddsById']['odds'][0]['odds']
            
            if odds:
                return float(odds[0]['value']), float(odds[1]['value'])
        except Exception as e:
            logger.warning(f"Failed to get odds for match {match_id}: {str(e)}")
            
        return None

    @staticmethod
    def process_team_stats(
        raw_data: str, 
        team_name: str, 
        stat_type: str
    ) -> Optional[Tuple[str, str]]:
        """
        Process team statistics from raw data.
        
        Args:
            raw_data: Raw statistics data
            team_name: Team name to search for
            stat_type: Type of statistics (for logging)
            
        Returns:
            Tuple of (games, score) or None if not found
        """
        if not raw_data:
            return None
            
        data = raw_data.split('¬TN÷')
        if len(data) < 2:
            return None
            
        data.pop(0)
        
        for team_data in data:
            if team_name in team_data.split('¬TI÷')[0]:
                try:
                    games = team_data.split('¬TM÷')[1].split('¬')[0].replace(' ', '')
                    score = team_data.split('¬TG÷')[1].split('¬')[0].replace(' ', '')
                    
                    if games and int(games) >= MIN_GAMES_THRESHOLD:
                        return (games, score)
                except (IndexError, ValueError) as e:
                    logger.warning(f"Error processing {stat_type} stats: {str(e)}")
                    
        return None

    @staticmethod
    def get_match_stats(match_id: str, team1: str, team2: str) -> Dict:
        """
        Get statistics for a match.
        
        Args:
            match_id: Match identifier
            team1: First team name
            team2: Second team name
            
        Returns:
            Dictionary with all collected statistics
        """
        stats = {
            'k1_score': None,
            'k2_score': None,
            'k1_score_home': None,
            'k2_score_home': None,
            'k1_score_away': None,
            'k2_score_away': None
        }
        
        # Get general stats
        try:
            url = f'{BASE_STATS_URL}/df_to_1_{match_id}_1'
            response = FlashScore.make_request(url)
            stats['k1_score'] = FlashScore.process_team_stats(response.text, team1, "general")
            stats['k2_score'] = FlashScore.process_team_stats(response.text, team2, "general")
        except Exception as e:
            logger.warning(f"Failed to get general stats for match {match_id}: {str(e)}")

        # Get home stats
        try:
            url = f'{BASE_STATS_URL}/df_to_1_{match_id}_2'
            response = FlashScore.make_request(url)
            stats['k1_score_home'] = FlashScore.process_team_stats(response.text, team1, "home")
            stats['k2_score_home'] = FlashScore.process_team_stats(response.text, team2, "home")
        except Exception as e:
            logger.warning(f"Failed to get home stats for match {match_id}: {str(e)}")

        # Get away stats
        try:
            url = f'{BASE_STATS_URL}/df_to_1_{match_id}_3'
            response = FlashScore.make_request(url)
            stats['k1_score_away'] = FlashScore.process_team_stats(response.text, team1, "away")
            stats['k2_score_away'] = FlashScore.process_team_stats(response.text, team2, "away")
        except Exception as e:
            logger.warning(f"Failed to get away stats for match {match_id}: {str(e)}")

        return stats

    @staticmethod
    def get_basketball_matches_info(day_offset: int) -> List[Dict]:
        """
        Get detailed information about basketball matches for specified day.
        
        Args:
            day_offset: Day offset (0 - today, -1 - yesterday, 1 - tomorrow)
            
        Returns:
            List of dictionaries with complete match information
        """
        matches = FlashScore.get_matches(3, day_offset)
        if not matches:
            return []

        results = []
        logger.info(f"Processing {len(matches)} matches...")

        for i, match in enumerate(matches, 1):
            match_id, team1, team2, date, league = match
            logger.info(f"Processing match {i}/{len(matches)}: {team1} vs {team2} (ID: {match_id})")

            match_data = {
                'match_id': match_id,
                'team_1': team1,
                'team_2': team2,
                'datetime': date,
                'league': league,
                'k_1': None,
                'k_2': None
            }

            # Get odds
            odds = FlashScore.get_odds(match_id)
            if not odds:
                logger.info(f"Skipping match {match_id} - no odds available")
                continue
                
            match_data['k_1'], match_data['k_2'] = odds

            # Get statistics
            stats = FlashScore.get_match_stats(match_id, team1, team2)
            match_data.update(stats)

            # Check if all required stats are available
            if all(match_data.get(key) for key in [
                'k1_score', 'k2_score',
                'k1_score_home', 'k2_score_home',
                'k1_score_away', 'k2_score_away'
            ]):
                results.append(match_data)
            else:
                logger.info(f"Skipping match {match_id} - incomplete statistics")

        logger.info(f"Successfully processed {len(results)} matches with complete data")
        return results


if __name__ == '__main__':
    logger.info("Starting FlashScore data collection")
    matches_info = FlashScore.get_basketball_matches_info(0)
    logger.info(f"Collected data for {len(matches_info)} matches")
    print(matches_info)