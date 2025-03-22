from pywebio.platform import config
from pywebio.input import input, DATE, FLOAT, actions, input_group
from pywebio.output import put_info, put_table, put_progressbar, set_progressbar, use_scope, clear_scope, put_html, put_error, put_warning
from main import flashscore
from datetime import datetime

config(title="FlashScore 2.0", css_style="#output-container{margin: 0 auto; max-width: 1200px;} #input-cards{max-width: 1200px;}")

def check_date(date):
    if date == "":
        return "Заполните это поле"
    
def check_field(num):
    if num == None:
        return "Заполните это поле"
    elif num < 0:
        return "Не должно быть отрицательным числом"

def smart_monitor():
        while True:
            clear_scope('scope1')
            data = input_group("Настройки отбора", [
                input("За какой день вы хотите получить данные по играм", type=DATE, validate=check_date, name="date"),
                input("Коэффицент индиктора Тотал Больше 2.5", type=FLOAT, validate=check_field, name="coefficient")
            ])
            search_date = datetime.strptime(data["date"], '%Y-%m-%d')
            coefficient = float(data["coefficient"])
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
                    while True:
                        try:
                            detail = flashscore.get_total_goals(str(id[0]))
                            if detail:
                                break
                        except Exception as e:
                            with use_scope('scope1'):
                                put_warning(e)

                    k1_goal_home_sum = 0
                    k1_lost_home_sum = 0
                    k1_goal_away_sum = 0
                    k1_lost_away_sum = 0
                    k2_goal_home_sum = 0
                    k2_lost_home_sum = 0
                    k2_goal_away_sum = 0
                    k2_lost_away_sum = 0
                    for j in range (1, 6):
                        if 7 < len(detail[0]) and 7 < len(detail[1]):
                            try:
                                if detail[0][j][4] == 'home':
                                    k1_goal_home_sum += detail[0][j][2]
                                    k1_lost_home_sum += detail[0][j][3]
                                if detail[0][j][4] == 'away':
                                    k1_goal_away_sum += detail[0][j][3]
                                    k1_lost_away_sum += detail[0][j][2]
                            except:
                                k1_goal_home_sum = 0
                                k1_lost_home_sum = 0
                                k1_goal_away_sum = 0
                                k1_lost_away_sum = 0
                            
                            try:
                                if detail[1][j][4] == 'home':
                                    k2_goal_home_sum += detail[1][j][2]
                                    k2_lost_home_sum += detail[1][j][3]
                                if detail[1][j][4] == 'away':
                                    k2_goal_away_sum += detail[1][j][3]
                                    k2_lost_away_sum += detail[1][j][2]
                            except:
                                k2_goal_home_sum = 0
                                k2_lost_home_sum = 0
                                k2_goal_away_sum = 0
                                k2_lost_away_sum = 0

                    if (k1_goal_home_sum != 0
                        and k1_lost_home_sum != 0
                        and k1_goal_away_sum != 0
                        and k1_lost_away_sum != 0
                        and k2_goal_home_sum != 0
                        and k2_lost_home_sum != 0
                        and k2_goal_away_sum != 0
                        and k2_lost_away_sum != 0
                        ):

                        goal_k1_home = k1_goal_home_sum * 1.5
                        goal_k1_away = k1_goal_away_sum * 2
                        k1_gained_points = (goal_k1_home + goal_k1_away) / 5
                        lost_k1_home = k1_lost_home_sum * 1.5
                        lost_k1_away = k1_lost_away_sum * 2
                        k1_lost_points = (lost_k1_home + lost_k1_away) / 5
                        k1_points = (k1_gained_points + k1_lost_points) / 2

                        goal_k2_home = k2_goal_home_sum * 1.5
                        goal_k2_away = k2_goal_away_sum * 2
                        k2_gained_points = (goal_k2_home + goal_k2_away) / 5
                        lost_k2_home = k2_lost_home_sum * 1.5
                        lost_k2_away = k2_lost_away_sum * 2
                        k2_lost_points = (lost_k2_home + lost_k2_away) / 5
                        k2_points = (k2_gained_points + k2_lost_points) / 2

                        points = (k1_points + k2_points) / 2
                        #print(id[0], points)


                        if (float(points) > coefficient):

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
