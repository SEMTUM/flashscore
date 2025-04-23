import json
import requests
from datetime import datetime


headers = {"x-fsign": "SW9D1eZo"} # Ключ авторизации на сервере (Пока не менялся)

class flashscore:

    def get_matchs(day):
        feed = f'f_1_{day}_3_ru_5' # Переменная "day" отвечает за какой день мы хотим получить результат (0 - сегодня, -1 - вчера, 1 - завтра и т.п.) (f_1 - футбол)
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
            
                list_match.append([id_match, team_1, team_2, date, league]) # Выдает список матчей которые будут проходить в установленный день (ID, Команда 1, Команда 2, Дата матча, Лига)
        
        return list_match

    def get_details(match):
        url = f'https://46.ds.lsapp.eu/pq_graphql?_hash=dsof&eventId={match}&projectId=46' #(В переменную "match" подставляем ID матча по которому хотим получить сведения)
        response = requests.get(url=url, headers=headers)
        data = json.loads(response.text)

        try: # последняя игра первой команды
            result_1 = data["data"]["findEventById"]["eventParticipants"][0]["participants"][0]["participant"]["lastEvents"][0]["parentParticipantWinner"]["winner"]
            score_1_1 = data["data"]["findEventById"]["eventParticipants"][0]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][0]["stats"][0]["values"][0]["value"]
            score_1_2 = data["data"]["findEventById"]["eventParticipants"][0]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][1]["stats"][0]["values"][0]["value"]
            score_1 = score_1_1 + " : " + score_1_2
        except:
            result_1 = "none"
            score_1 = ""
        try: # последняя игра второй команды
            result_2 = data["data"]["findEventById"]["eventParticipants"][1]["participants"][0]["participant"]["lastEvents"][0]["parentParticipantWinner"]["winner"]
            score_2_1 = data["data"]["findEventById"]["eventParticipants"][1]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][0]["stats"][0]["values"][0]["value"]
            score_2_2 = data["data"]["findEventById"]["eventParticipants"][1]["participants"][0]["participant"]["lastEvents"][0]["eventParticipants"][1]["stats"][0]["values"][0]["value"]
            score_2 = score_2_1 + " : " + score_2_2
        except:
            result_2 = "none"
            score_2 = ""
        
        return result_1, result_2, score_1, score_2 # Выдает резельтат предыдущих игр каждой из команд и счёт
    
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
            if '~KB' in item.keys(): # [0] - последние игры 1 команды, [1] - последние игры 2 команды 
                list_match.append([item.get('~KB')])
                list_match[-1].append([])
            if 'KJ' in item.keys(): # [0][2-...][0] - название 1 команды 
                list_match[-1][-1].append(item.get('KJ'))
            if 'KK' in item.keys(): # [0][2-...][1] - название 2 команды 
                list_match[-1][-1].append(item.get('KK'))
            if 'KU' in item.keys() and item.get('KU') != '': # [0][2-...][2] - счёт 1 команды 
                list_match[-1][-1].append(int(item.get('KU')))
            if 'KT' in item.keys() and item.get('KT') != '': # [0][2-...][3] - счёт 2 команды 
                list_match[-1][-1].append(int(item.get('KT')))
            if 'KS' in item.keys(): # [0][2-...][4] - где играла команда
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
                    odds = item ['odds']
            for elem in odds:
                if float(elem['handicap']['value']) == 2.5 and elem['selection'] == 'OVER': 
                    return elem['value']
        except:
            return None



if __name__ == '__main__':
    print(flashscore.get_odds("f79xolZj"))