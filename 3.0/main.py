import json
import logging
from datetime import datetime
from time import sleep
from typing import List, Dict, Optional, Tuple
import requests

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('__main__')

# Константы
API_HEADERS = {"x-fsign": "SW9D1eZo"}
MAX_RETRIES = 3
RETRY_DELAY = 10
MIN_GAMES_THRESHOLD = 5

# API endpoints
BASE_FLASHSCORE_URL = "https://d.flashscorekz.com/x/feed"
BASE_ODDS_URL = "https://global.ds.lsapp.eu/odds/pq_graphql"
BASE_STATS_URL = "https://46.flashscore.ninja/46/x/feed"


class FlashScore:
    """Класс для взаимодействия с API FlashScore для получения спортивных данных."""

    @staticmethod
    def make_request(url: str) -> requests.Response:
        """
        Выполняет HTTP-запрос с логикой повторных попыток.
        
        Args:
            url: URL для запроса
            
        Returns:
            Объект Response
            
        Raises:
            Exception: После превышения максимального числа попыток
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url=url, headers=API_HEADERS)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                logger.warning(f"Попытка {attempt + 1} не удалась для URL {url}: {str(e)}")
                logger.info(f"Ожидание {RETRY_DELAY} секунд перед повторной попыткой...")
                sleep(RETRY_DELAY)

    @staticmethod
    def parse_match_data(raw_data: str) -> List[Dict]:
        """
        Парсит сырые данные о матчах из API FlashScore.
        
        Args:
            raw_data: Сырой текст ответа от API
            
        Returns:
            Список распарсенных словарей с данными о матчах
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
        Получает матчи для указанного вида спорта и дня.
        
        Args:
            sport_id: Идентификатор вида спорта (3 - баскетбол)
            day_offset: Смещение дня (0 - сегодня, -1 - вчера, 1 - завтра)
            
        Returns:
            Список кортежей с данными о матчах (id, команда1, команда2, дата, лига)
        """
        feed = f'f_{sport_id}_{day_offset}_3_ru_5'
        url = f'{BASE_FLASHSCORE_URL}/{feed}'
        
        try:
            response = FlashScore.make_request(url)
            data_list = FlashScore.parse_match_data(response.text)
        except Exception as e:
            logger.error(f"Ошибка при получении матчей: {str(e)}")
            return []

        matches = []
        current_league = "Неизвестно"
        
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
                    logger.warning(f"Ошибка при разборе данных матча: {str(e)}")

        logger.info(f"Успешно получено {len(matches)} матчей")
        return matches

    @staticmethod
    def get_odds(match_id: str) -> Optional[Tuple[float, float]]:
        """
        Получает коэффициенты для конкретного матча.
        
        Args:
            match_id: Идентификатор матча
            
        Returns:
            Кортеж (коэффициент1, коэффициент2) или None, если недоступно
        """
        url = f'{BASE_ODDS_URL}?_hash=ope&eventId={match_id}&projectId=46&geoIpCode=RU&geoIpSubdivisionCode=RU'
        
        try:
            response = FlashScore.make_request(url)
            data = json.loads(response.text)
            odds = data['data']['findPrematchOddsById']['odds'][0]['odds']
            
            if odds:
                return float(odds[0]['value']), float(odds[1]['value'])
        except Exception as e:
            logger.warning(f"Не удалось получить коэффициенты для матча {match_id}: {str(e)}")
            
        return None

    @staticmethod
    def process_team_stats(
        raw_data: str, 
        team_name: str, 
        stat_type: str
    ) -> Optional[Tuple[str, str]]:
        """
        Обрабатывает статистику команды из сырых данных.
        
        Args:
            raw_data: Сырые данные статистики
            team_name: Название команды для поиска
            stat_type: Тип статистики (для логгирования)
            
        Returns:
            Кортеж (игры, счет) или None, если не найдено
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
                    logger.warning(f"Ошибка при обработке статистики {stat_type}: {str(e)}")
                    
        return None

    @staticmethod
    def get_match_stats(match_id: str, team1: str, team2: str) -> Dict:
        """
        Получает статистику для матча.
        
        Args:
            match_id: Идентификатор матча
            team1: Название первой команды
            team2: Название второй команды
            
        Returns:
            Словарь со всей собранной статистикой
        """
        stats = {
            'k1_score': None,
            'k2_score': None,
            'k1_score_home': None,
            'k2_score_home': None,
            'k1_score_away': None,
            'k2_score_away': None
        }
        
        # Получение общей статистики
        try:
            url = f'{BASE_STATS_URL}/df_to_1_{match_id}_1'
            response = FlashScore.make_request(url)
            stats['k1_score'] = FlashScore.process_team_stats(response.text, team1, "общая")
            stats['k2_score'] = FlashScore.process_team_stats(response.text, team2, "общая")
        except Exception as e:
            logger.warning(f"Не удалось получить общую статистику для матча {match_id}: {str(e)}")

        # Получение домашней статистики
        try:
            url = f'{BASE_STATS_URL}/df_to_1_{match_id}_2'
            response = FlashScore.make_request(url)
            stats['k1_score_home'] = FlashScore.process_team_stats(response.text, team1, "домашняя")
            stats['k2_score_home'] = FlashScore.process_team_stats(response.text, team2, "домашняя")
        except Exception as e:
            logger.warning(f"Не удалось получить домашнюю статистику для матча {match_id}: {str(e)}")

        # Получение гостевой статистики
        try:
            url = f'{BASE_STATS_URL}/df_to_1_{match_id}_3'
            response = FlashScore.make_request(url)
            stats['k1_score_away'] = FlashScore.process_team_stats(response.text, team1, "гостевая")
            stats['k2_score_away'] = FlashScore.process_team_stats(response.text, team2, "гостевая")
        except Exception as e:
            logger.warning(f"Не удалось получить гостевую статистику для матча {match_id}: {str(e)}")

        return stats

    @staticmethod
    def get_basketball_matches_info(day_offset: int) -> List[Dict]:
        """
        Получает подробную информацию о баскетбольных матчах для указанного дня.
        
        Args:
            day_offset: Смещение дня (0 - сегодня, -1 - вчера, 1 - завтра)
            
        Returns:
            Список словарей с полной информацией о матчах
        """
        matches = FlashScore.get_matches(3, day_offset)
        if not matches:
            return []

        results = []
        logger.info(f"Обработка {len(matches)} матчей...")

        for i, match in enumerate(matches, 1):
            match_id, team1, team2, date, league = match
            logger.info(f"Обработка матча {i}/{len(matches)}: {team1} против {team2} (ID: {match_id})")

            match_data = {
                'match_id': match_id,
                'team_1': team1,
                'team_2': team2,
                'datetime': date,
                'league': league,
                'k_1': None,
                'k_2': None
            }

            # Получение коэффициентов
            odds = FlashScore.get_odds(match_id)
            if not odds:
                logger.info(f"Пропуск матча {match_id} - коэффициенты недоступны")
                continue
                
            match_data['k_1'], match_data['k_2'] = odds

            # Получение статистики
            stats = FlashScore.get_match_stats(match_id, team1, team2)
            match_data.update(stats)

            # Проверка наличия всей необходимой статистики
            if all(match_data.get(key) for key in [
                'k1_score', 'k2_score',
                'k1_score_home', 'k2_score_home',
                'k1_score_away', 'k2_score_away'
            ]):
                results.append(match_data)
            else:
                logger.info(f"Пропуск матча {match_id} - неполная статистика")

        logger.info(f"Успешно обработано {len(results)} матчей с полными данными")
        return results


if __name__ == '__main__':
    logger.info("Начало сбора данных FlashScore")
    matches_info = FlashScore.get_basketball_matches_info(0)
    logger.info(f"Собраны данные для {len(matches_info)} матчей")
    print(matches_info)