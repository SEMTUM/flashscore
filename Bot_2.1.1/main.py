import json
import requests
from datetime import datetime, timedelta
import telebot
import time

headers = {"x-fsign": "SW9D1eZo"}  # Ключ авторизации на сервера

# Глобальный список для хранения уже отправленных матчей
sent_matches = []

class flashscore:

    def get_matchs(day):
        feed = f'f_1_{day}_3_ru_5'  # f_1 - футбол, day - день (0 - сегодня)
        url = f'https://d.flashscorekz.com/x/feed/{feed}'
        response = requests.get(url=url, headers=headers)
        data = response.text.split('¬')

        data_list = [{}]
        list_match = []

        for item in data:
            key = item.split('÷')[0]
            value = item.split('÷')[-1]

            if '~' in key:
                data_list.append({key: value})
            else:
                data_list[-1].update({key: value})
        league = "none"
        for game in data_list:
            if 'ZA' in list(game.keys())[0]:
                league = game.get("~ZA")
            if 'AA' in list(game.keys())[0]:
                date = datetime.fromtimestamp(int(game.get("AD")))
                team_1 = game.get("AE")
                team_2 = game.get("AF")
                id_match = game.get("~AA")
            
                list_match.append([id_match, team_1, team_2, date, league])
        
        return list_match

    def get_details(match):
        url = f'https://46.ds.lsapp.eu/pq_graphql?_hash=dsof&eventId={match}&projectId=46'
        response = requests.get(url=url, headers=headers)
        data = json.loads(response.text)

        try:
            result_1 = data["data"]["findEventById"]["eventParticipants"][0]["participants"][0]["participant"]["lastEvents"][0]["parentParticipantWinner"]["winner"]
            score_1_1 = data["data"]["findEventById"]["eventParticipants"][0]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][0]["stats"][0]["values"][0]["value"]
            score_1_2 = data["data"]["findEventById"]["eventParticipants"][0]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][1]["stats"][0]["values"][0]["value"]
            score_1 = score_1_1 + " : " + score_1_2
        except:
            result_1 = "none"
            score_1 = ""
        try:
            result_2 = data["data"]["findEventById"]["eventParticipants"][1]["participants"][0]["participant"]["lastEvents"][0]["parentParticipantWinner"]["winner"]
            score_2_1 = data["data"]["findEventById"]["eventParticipants"][1]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][0]["stats"][0]["values"][0]["value"]
            score_2_2 = data["data"]["findEventById"]["eventParticipants"][1]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][1]["stats"][0]["values"][0]["value"]
            score_2 = score_2_1 + " : " + score_2_2
        except:
            result_2 = "none"
            score_2 = ""
        
        return result_1, result_2, score_1, score_2
    
    def get_total_goals(match):
        url = f'https://46.flashscore.ninja/46/x/feed/df_hh_1_{match}'
        response = requests.get(url=url, headers=headers)
        data = response.text.split('¬')

        data_list = [{}]
        list_match = []

        for item in data:
            key = item.split('÷')[0]
            value = item.split('÷')[-1]

            if '~' in key:
                data_list.append({key: value})
            else:
                data_list[-1].update({key: value})
        i = -1
        for item in data_list:
            if '~KB' in item.keys():
                list_match.append([item.get('~KB')])
                list_match[-1].append([])
            if 'KJ' in item.keys():
                list_match[-1][-1].append(item.get('KJ'))
            if 'KK' in item.keys():
                list_match[-1][-1].append(item.get('KK'))
            if 'KU' in item.keys() and item.get('KU') != '':
                list_match[-1][-1].append(int(item.get('KU')))
            if 'KT' in item.keys() and item.get('KT') != '':
                list_match[-1][-1].append(int(item.get('KT')))
            if 'KS' in item.keys():
                list_match[-1][-1].append(item.get('KS'))
                list_match[-1].append([])
        
        return list_match
    
    def get_odds(match_id):
        url = f'https://global.ds.lsapp.eu/odds/pq_graphql?_hash=oce&eventId={match_id}&projectId=46&geoIpCode=RU&geoIpSubdivisionCode=RU'
        response = requests.get(url=url, headers=headers)
        data = json.loads(response.text)['data']['findOddsByEventId']['odds']
        try:
            for item in data:
                if item['bettingType'] == 'OVER_UNDER' and item['bettingScope'] == 'FULL_TIME':
                    odds = item['odds']
            for elem in odds:
                if float(elem['handicap']['value']) == 2.5 and elem['selection'] == 'OVER': 
                    return elem['value']
        except:
            return None

def analyze_matches():
    global sent_matches
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time, 'Чистим список!')  
    
    # Удаляем матчи старше 2 дней
    current_time = datetime.now()
    sent_matches = [match for match in sent_matches 
                   if (current_time - match['match_time']) <= timedelta(days=2)]
                                             
    
    # Инициализация переменной для хранения результатов
    list_live = []
    day = 0
    coefficient = 3
    
    # Получаем список матчей на указанный день
    search_list = flashscore.get_matchs(day)
    
    # Обрабатываем каждый матч
    for match in search_list:
        match_id = match[0]
        
        # Получаем статистику по голам для матча
        while True:
            try:
                detail = flashscore.get_total_goals(str(match_id))
                if detail:
                    break
            except Exception as e:
                print(f"Ошибка при получении данных для матча {match_id}: {e}")
                continue

        # Инициализация переменных для подсчета статистики
        k1_goal_home_sum = 0
        k1_lost_home_sum = 0
        k1_goal_away_sum = 0
        k1_lost_away_sum = 0
        k2_goal_home_sum = 0
        k2_lost_home_sum = 0
        k2_goal_away_sum = 0
        k2_lost_away_sum = 0
        
        # Анализ последних 5 матчей для обеих команд
        for j in range(1, 6):
            if 7 < len(detail[0]) and 7 < len(detail[1]):
                try:
                    if detail[0][j][4] == 'home':
                        k1_goal_home_sum += detail[0][j][2]
                        k1_lost_home_sum += detail[0][j][3]
                    if detail[0][j][4] == 'away':
                        k1_goal_away_sum += detail[0][j][3]
                        k1_lost_away_sum += detail[0][j][2]
                except:
                    pass
                
                try:
                    if detail[1][j][4] == 'home':
                        k2_goal_home_sum += detail[1][j][2]
                        k2_lost_home_sum += detail[1][j][3]
                    if detail[1][j][4] == 'away':
                        k2_goal_away_sum += detail[1][j][3]
                        k2_lost_away_sum += detail[1][j][2]
                except:
                    pass

        # Проверяем, что все данные есть
        if (k1_goal_home_sum != 0 and k1_lost_home_sum != 0 and k1_goal_away_sum != 0 and k1_lost_away_sum != 0 and
            k2_goal_home_sum != 0 and k2_lost_home_sum != 0 and k2_goal_away_sum != 0 and k2_lost_away_sum != 0):
            
            # Расчет показателей
            goal_k1_home = k1_goal_home_sum * 1.5
            goal_k1_away = k1_goal_away_sum * 2
            k1_gained_points = (goal_k1_home + goal_k1_away) / 5
            lost_k1_home = k1_lost_home_sum * 1.5
            lost_k1_away = k1_lost_away_sum * 1
            k1_lost_points = (lost_k1_home + lost_k1_away) / 5
            k1_points = (k1_gained_points + k1_lost_points) / 2

            goal_k2_home = k2_goal_home_sum * 1.5
            goal_k2_away = k2_goal_away_sum * 2
            k2_gained_points = (goal_k2_home + goal_k2_away) / 5
            lost_k2_home = k2_lost_home_sum * 1.5
            lost_k2_away = k2_lost_away_sum * 1
            k2_lost_points = (lost_k2_home + lost_k2_away) / 5
            k2_points = (k2_gained_points + k2_lost_points) / 2
            
            points = (k1_points + k2_points) / 2
            
            if float(points) > coefficient:
                tb2_5 = flashscore.get_odds(match_id)
                
                if datetime.now() <= match[3] and tb2_5 is not None and float(tb2_5) >= 1.7:
                    date_str = match[3].strftime('%d.%m.%Y')
                    time_str = match[3].strftime('%H:%M')
                    
                    # Формируем уникальный ключ для матча
                    match_key = f"{match[1]}_{match[2]}_{date_str}"
                    
                    # Проверяем, есть ли уже такой матч в списке
                    if not any(m['key'] == match_key for m in sent_matches):
                        list_live.append({
                            'key': match_key,
                            'date_str': date_str,
                            'time_str': time_str,
                            'league': match[4],
                            'teams': f"{match[1]} - {match[2]}",
                            'odds': tb2_5,
                            'index': round(points, 1),
                            'match_time': match[3]
                        })
    
    return list_live

# Инициализация бота
bot = telebot.TeleBot('7987890606:AAHfqZ_1ymnTpxEMEPWgxlaJJas5qRCzoKg')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Начинаю анализ матчей! 😎")
    
    global sent_matches
    
    while True:
        try:
            results = analyze_matches()
            
            if results:
                new_matches = [m for m in results if m['key'] not in [sm['key'] for sm in sent_matches]]
                
                if new_matches:
                    for match in new_matches:
                        response = (f'''
🏆 {match['league']}

⚽️ {match['teams']}

--------------------------------------------
⏰ Время матча: {match['date_str']}
--------------------------------------------
Индекс прохода ТБ: {match['index']}
--------------------------------------------

🔥 Прогноз: ТБ 2.5 : {match['odds']}

''' 
                           
 
                                                                  )
                        bot.send_message(message.chat.id, response)
                        
                        # Добавляем матч в список отправленных
                        sent_matches.append(match)
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S")
                        print(current_time, 'Сигнал!')
                else:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print(current_time, 'Не найдено!')
            else:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(current_time, 'Не найдено!')
            
            # Пауза перед следующим анализом (1 час)
            time.sleep(60)
            
        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")
            time.sleep(60)

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)