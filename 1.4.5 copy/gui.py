from pywebio.platform import config
from pywebio.input import input, DATE, FLOAT, actions, input_group
from pywebio.output import put_info, put_table, put_progressbar, set_progressbar, use_scope, clear_scope, put_html, put_error
from main import flashscore
from datetime import datetime

config(title="FlashScore", css_style="#output-container{margin: 0 auto; max-width: 1200px;} #input-cards{max-width: 1200px;}")

def check_date(date):
    if date == "":
        return "Заполните это поле"
    
def check_field(num):
    if num == None:
        return "Заполните это поле"
    elif num < 0:
        return "Количество голов не должно быть отрицательным числом"

def smart_monitor():
        while True:
            clear_scope('scope1')
            data = input_group("Настройки отбора", [
                input("За какой день вы хотите получить данные по играм", type=DATE, validate=check_date, name="date"),
                input("Команда 1 забивала в среднем за матч более:", type=FLOAT, validate=check_field, name="k1_goal"),
                input("Дома более:", type=FLOAT, validate=check_field, name="k1_goal_home"),
                input("Команда 1 пропускала в среднем за матч более:", type=FLOAT, validate=check_field, name="k1_lost"),
                input("Дома более:", type=FLOAT, validate=check_field, name="k1_lost_home"),
                input("Команда 2 забивала в среднем за матч более:", type=FLOAT, validate=check_field, name="k2_goal"),
                input("В гостях более:", type=FLOAT, validate=check_field, name="k2_goal_away"),
                input("Команда 2 пропускала в среднем за матч более:", type=FLOAT, validate=check_field, name="k2_lost"),
                input("В гостях более:", type=FLOAT, validate=check_field, name="k2_lost_away")
            ])
            search_date = datetime.strptime(data["date"], '%Y-%m-%d')
            k1_goal = data["k1_goal"]
            k1_goal_home = data["k1_goal_home"]
            k1_lost = data["k1_lost"]
            k1_lost_home = data["k1_lost_home"]
            k2_goal = data["k2_goal"]
            k2_goal_away = data["k2_goal_away"]
            k2_lost = data["k2_lost"]
            k2_lost_away = data["k2_lost_away"]
            table_data_list = []
            now = str(datetime.now())[:10]
            today = datetime.strptime(now, '%Y-%m-%d')
            num_days = (today - search_date).days
            if int(num_days) < 0:
                num = abs(int(num_days))
            else:
                num = int("-" + str(num_days))
            with use_scope('scope1'):
                put_info("Пожалуйста подождите... Результат появится на экране)")
                put_progressbar('bar')
                search_list = flashscore.get_matchs(num)
                i = 0
                n = len(search_list)
                for id in search_list:
                    i = i + 1
                    set_progressbar('bar', i / n)
                    detail = flashscore.get_total_goals(str(id[0]))
                    command_1 = detail[0][0].split(": ")[1]
                    command_2 = detail[1][0].split(": ")[1]
                    k1_goal_sum = 0
                    k1_lost_sum = 0
                    k2_goal_sum = 0
                    k2_lost_sum = 0
                    k1_goal_home_sum = 0
                    k1_lost_home_sum = 0
                    k2_goal_away_sum = 0
                    k2_lost_away_sum = 0
                    for j in range (1, 11):
                        if 12 < len(detail[0]) and 12 < len(detail[1]):
                            try:
                                if command_1 in detail[0][j][0]:
                                    k1_goal_sum += detail[0][j][2]
                                    k1_lost_sum += detail[0][j][3]
                                else:
                                    k1_goal_sum += detail[0][j][3]
                                    k1_lost_sum += detail[0][j][2]
                            except:
                                k1_goal_sum = 0
                                k1_lost_sum = 0
                            
                            try:
                                if command_2 in detail[1][j][0]:
                                    k2_goal_sum += detail[1][j][2]
                                    k2_lost_sum += detail[1][j][3]
                                else:
                                    k2_goal_sum += detail[1][j][3]
                                    k2_lost_sum += detail[1][j][2]
                            except:
                                k2_goal_sum = 0
                                k2_lost_sum = 0

                        if 12 < len(detail[3]) and 12 < len(detail[5]):
                            try:
                                if command_1 in detail[3][j][0]:
                                    k1_goal_home_sum += detail[3][j][2]
                                    k1_lost_home_sum += detail[3][j][3]
                                else:
                                    k1_goal_home_sum += detail[3][j][3]
                                    k1_lost_home_sum += detail[3][j][2]
                            except:
                                k1_goal_home_sum = 0
                                k1_lost_home_sum = 0
                            
                            try:
                                if command_2 in detail[5][j][0]:
                                    k2_goal_away_sum += detail[5][j][2]
                                    k2_lost_away_sum += detail[5][j][3]
                                else:
                                    k2_goal_away_sum += detail[5][j][3]
                                    k2_lost_away_sum += detail[5][j][2]
                            except:
                                k2_goal_away_sum = 0
                                k2_lost_away_sum = 0
                    
                    if (k1_goal_sum != 0 
                        and k1_lost_sum != 0 
                        and k1_goal_home_sum != 0
                        and k1_lost_home_sum != 0
                        and k2_goal_sum != 0
                        and k2_lost_sum != 0
                        and k2_goal_away_sum != 0
                        and k2_lost_away_sum != 0
                        ):

                        if (k1_goal <= k1_goal_sum / 10
                            and k1_lost <= k1_lost_sum / 10
                            and k1_goal_home <= k1_goal_home_sum / 10
                            and k1_lost_home <= k1_lost_home_sum / 10
                            and k2_goal <= k2_goal_sum / 10
                            and k2_lost <= k2_lost_sum / 10
                            and k2_goal_away <= k2_goal_away_sum / 10
                            and k2_lost_away <= k2_lost_away / 10
                            ):

                            link = f"https://www.flashscorekz.com/match/{id[0]}/#/match-summary"
                            name = id[1] + " - " + id[2]
                            commands = '<a href="' + link + '" target="_blank">' + name + '</a>'

                            if  datetime.now() < id[3]:
                                table_data_list.append([
                                    id[3].date(),
                                    id[3].time(),
                                    id[4],
                                    put_html(commands)
                                    ])
            
            clear_scope('scope1')
            if table_data_list != []:
                with use_scope('scope1'):
                    put_table(table_data_list, header=[
                        "Дата",
                        "Время",
                        "Лига",
                        "Матч"
                        ])
            else:
                with use_scope('scope1'):
                    put_error("Нет данных по указанным параметрам!")

            actions(buttons=["Новый запрос"])

if __name__ == '__main__':
    smart_monitor()
