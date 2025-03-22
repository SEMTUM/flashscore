from pywebio.input import input, DATE, actions, checkbox, input_group
from pywebio.output import put_info, put_table, put_progressbar, set_progressbar, use_scope, clear_scope, put_link
from main import flashscore
from datetime import datetime

def check_date(date):
    if date == "":
        return "Заполните это поле"

def smart_monitor():
        while True:
            clear_scope('scope1')
            data = input_group("Настройки отбора",[
                input("За какой день вы хотите получить данные по играм", type=DATE, validate=check_date, name="date"),
                checkbox(options={"Добавить фильтр по счёту (Только 0:0)"}, name="select")
            ])
            search_date = datetime.strptime(data["date"], '%Y-%m-%d')
            selection = data["select"]
            selectionn_list = ["0 : 0"]
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
                    res_1, res_2, scr_1, scr_2 = flashscore.get_details(str(id[0]))
                    if res_1 == res_2 == "draw":
                        if selection == []: # Фильтр ("Добавить фильтр по счёту (Только 0:0 или 1:1)")
                            table_data_list.append(
                                [put_link("Ссылка на матч", f"https://www.flashscorekz.com/match/{id[0]}/#/match-summary", new_window=True),
                                 scr_1,
                                 scr_2,
                                 id[3],
                                 id[1] + " - " + id[2]]
                                 )
                        else:
                            if (scr_1 in selectionn_list) and (scr_2 in selectionn_list) and (scr_1 != "1 : 1" or scr_2 != "1 : 1"):
                                table_data_list.append(
                                    [put_link("Ссылка на матч", f"https://www.flashscorekz.com/match/{id[0]}/#/match-summary", new_window=True),
                                     scr_1,
                                     scr_2,
                                     id[3],
                                     id[1] + " - " + id[2]]
                                     )
                put_table(table_data_list, header=[
                    'ID матча',
                    'Результат последней игры 1 команды',
                    'Результат последней игры 2 команды',
                    "Дата будущей игры",
                    "Команды соперники"
                    ])

            actions(buttons=["Новый запрос"])

if __name__ == '__main__':
    smart_monitor()
