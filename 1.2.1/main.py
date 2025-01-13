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
        #print(data_list)
        for game in data_list:
            if 'AA' in list(game.keys())[0]:
                date = datetime.fromtimestamp(int(game.get("AD")))
                team_1 = game.get("AE")
                team_2 = game.get("AF")
                id_match = game.get("~AA")
            
                list_match.append([id_match, team_1, team_2, date]) # Выдает список матчей которые будут проходить в установленный день (ID, Команда 1, Команда 2, Дата матча)
        
        return list_match

    def get_details(match):
        url = f'https://46.ds.lsapp.eu/pq_graphql?_hash=dsof&eventId={match}&projectId=46' #(В переменную "match" подставляем ID матча по которому хотим получить сведения)
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
        
        return result_1, result_2, score_1, score_2 # Выдает резельтат предыдущих игр каждой из команд и счёт


if __name__ == '__main__':
    #search_list = flashscore.get_matchs(0)
    #for id in search_list:
    #    res_1, res_2, scr_1, scr_2 = flashscore.get_details(str(id[0]))
    #    if res_1 == res_2 == "draw":
    #        print(id[0], "(" + res_1, "Счёт: " + scr_1 + ")", "(" + res_2, "Счёт: " + scr_2 + ")", id[3], id[1] + " - " + id[2])
    #print(flashscore.get_matchs(1))
    pass