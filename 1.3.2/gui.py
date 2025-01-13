from pywebio.input import input, DATE, NUMBER, actions, checkbox, input_group
from pywebio.output import put_info, put_table, put_progressbar, set_progressbar, use_scope, clear_scope, put_link
from main import flashscore
from datetime import datetime

def check_date(date):
    if date == "":
        return "Заполните это поле"

def check_min_goals(min_goals):
    if min_goals == None:
        return "Заполните это поле"
    
def check_max_goals(max_goals):
    if max_goals == None:
        return "Заполните это поле"


def smart_monitor():
        while True:
            clear_scope('scope1')
            data = input_group("Настройки отбора",[
                input("За какой день вы хотите получить данные по играм", type=DATE, validate=check_date, name="date"),
                input('Минимальное количество голов за 10 матчей', type=NUMBER, validate=check_min_goals, name='min_goals'),
                input('Максимальное количество голов за 10 матчей', type=NUMBER, validate=check_max_goals, name='max_goals')
            ])
            search_date = datetime.strptime(data["date"], '%Y-%m-%d')
            min_goals = data["min_goals"]
            max_goals = data["max_goals"]
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
                    k1 = 0
                    k1_home = 0
                    k2 = 0
                    k2_away = 0

                    for j in range (1, 11):
                        if 12 < len(detail[0]) and 12 < len(detail[1]):
                            try:
                                k1 += detail[0][j][2] + detail[0][j][3]
                            except:
                                k1 += 0
                            try:
                                k2 += detail[1][j][2] + detail[1][j][3]
                            except:
                                k2 += 0
                        else:
                            k1 = k2 = 0

                        if 12 < len(detail[3]) and 12 < len(detail[5]):
                            try:
                                k1_home += detail[3][j][2] + detail[3][j][3]
                            except:
                                k1_home += 0
                            try:
                                k2_away += detail[5][j][2] + detail[5][j][3]
                            except:
                                k2_away += 0
                        else:
                            k1_home = k2_away = 0
                    
                    if min_goals <= k1 <= max_goals and min_goals <= k2 <= max_goals and min_goals <= k1_home <= max_goals and min_goals <= k2_away <= max_goals and (k1 != 0 and k2 != 0 and k1_home != 0 and k2_away != 0):
                        table_data_list.append(
                            [put_link("Ссылка на матч", f"https://www.flashscorekz.com/match/{id[0]}/#/match-summary", new_window=True),
                            k1,
                            k1_home,
                            k2,
                            k2_away,
                            id[3],
                            id[1] + " - " + id[2]]
                            )
                
                put_table(table_data_list, header=[
                    'ID матча',
                    'Команда 1',
                    'К1 - Дома',
                    "Команда 2",
                    "К2 - В гостях",
                    "Дата и время",
                    "Команды-соперники"
                    ])

            actions(buttons=["Новый запрос"])

if __name__ == '__main__':
    smart_monitor()
