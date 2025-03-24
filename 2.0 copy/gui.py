from pywebio.platform import config
from pywebio.input import input, DATE, FLOAT, actions, input_group
from pywebio.output import put_table, put_progressbar, set_progressbar, use_scope, clear_scope, put_html, put_error, put_warning, put_success
from main import flashscore
from datetime import datetime
from pywebio.session import run_js
from pywebio.exceptions import SessionClosedException


css = '''
    [data-pywebio-input-label] {
        background: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    
    [data-pywebio-input-label]::before {
        content: '';
        display: inline-block;
        width: 24px;
        height: 24px;
        background-size: contain;
    }
    
    #date-label::before {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%233498db" d="M19,4H5C3.89,4 3,4.89 3,6V18A2,2 0 0,0 5,20H19A2,2 0 0,0 21,18V6C21,4.89 20.1,4 19,4M19,18H5V8H19V18M12,9H7V14H12V9"/></svg>');
    }
    
    #coefficient-label::before {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%233498db" d="M14.43,10C14.6,10.74 14.22,11.5 13.5,11.7C12.3,12.07 11.03,11.24 10.63,10H7V13H9.06C9.15,13.34 9.23,13.69 9.3,14.08C9.39,14.56 9.5,15.06 9.59,15.54C9.71,16.1 9.3,16.71 8.73,16.9C8.12,17.11 7.5,16.72 7.3,16.11C6.58,14.19 6,12.28 6,12.28V10H4V17H11.38C11.5,16.21 11.82,15.5 12.3,14.93C12.91,14.2 13.86,13.82 14.79,14.05C16.5,14.45 17.24,16.35 16.41,17.8C15.96,18.5 15.27,18.84 14.54,19H20V10H14.43Z"/></svg>');
    }
    
    input {
        padding: 10px 15px !important;
        border: 2px solid #bdc3c7 !important;
        border-radius: 6px !important;
        margin-top: 8px !important;
    }
    #output-container{
        margin: 0 auto;
        max-width: 1200px;
    } 
    #input-cards{
        max-width: 1200px;
    }
'''

config(title="FlashScore 2.0 (10 игр)", css_style=css)

def check_date(date):
    if date == "":
        return "Заполните это поле"
    
def check_field(num):
    if num == None:
        return "Заполните это поле"
    elif num < 0:
        return "Не должно быть отрицательным числом"

def smart_monitor():
        run_js('''
                    document.querySelector('footer').innerHTML = 
                        '<div style="font-size:0.9em">' +
                        '<span style="color:#e74c3c"><a href="https://t.me/@Steven_92">@Steven_92</a></span> | ' +
                        'Напишем любую программу для вас ' + '| Powered by <a href="https://pywebio.readthedocs.io/">PyWebIO</a>'
                        '</div>';
                    ''')
        while True:
            try:
                with use_scope('scope1', clear=True):
                    put_html('<div style="font-size:1.2rem; color:#2c3e50; margin-bottom:15px;">⚙️ Настройки отбора</div>')

                    data = input_group(
                        inputs=[
                            # Поле даты
                            input(label="Дата анализа", 
                                type=DATE, 
                                name="date",
                                validate=check_date,
                                placeholder="ДД.ММ.ГГГГ",
                                help_text="Выберите дату для анализа матчей",
                                required=True
                            ),
                            
                            # Поле коэффициента
                            input(label="Индекс Тотал Больше", 
                                type=FLOAT, 
                                name="coefficient",
                                validate=check_field,
                                placeholder="Например - 2.5",
                                help_text="Индекс количества голов",
                                datalist=['1.5', '2', '2.5', '3', '3.5', '4', '4.5'],
                                required=True
                            )
                        ]
                    )
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
                with use_scope('scope1', clear=True):
                    # Стилизованное сообщение о загрузке
                    put_html('''
                        <div style="
                            background: #e3f2fd;
                            border-left: 4px solid #2196f3;
                            padding: 15px;
                            margin: 10px 0;
                            border-radius: 4px;
                            display: flex;
                            align-items: center;
                            gap: 12px;
                        ">
                            <style>
                                @keyframes spin {
                                    0% { transform: rotate(0deg); }
                                    100% { transform: rotate(360deg); }
                                }
                                .loading-icon {
                                    animation: spin 1.2s linear infinite;
                                    transform-origin: center;
                                }
                            </style>
                            <div class="loading-icon">
                                <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                                    <path fill="#2196f3" d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
                                </svg>
                            </div>
                            <div style="font-weight:500; color:#1565c0">Идет поиск совпадений... Результаты появятся здесь</div>
                        </div>
                    ''')
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
                        for j in range (1, 11):
                            if 12 < len(detail[0]) and 12 < len(detail[1]):
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
                            k1_gained_points = (goal_k1_home + goal_k1_away) / 10
                            lost_k1_home = k1_lost_home_sum * 1.5
                            lost_k1_away = k1_lost_away_sum * 1
                            k1_lost_points = (lost_k1_home + lost_k1_away) / 10
                            k1_points = (k1_gained_points + k1_lost_points) / 2

                            goal_k2_home = k2_goal_home_sum * 1.5
                            goal_k2_away = k2_goal_away_sum * 2
                            k2_gained_points = (goal_k2_home + goal_k2_away) / 10
                            lost_k2_home = k2_lost_home_sum * 1.5
                            lost_k2_away = k2_lost_away_sum * 1
                            k2_lost_points = (lost_k2_home + lost_k2_away) / 10
                            k2_points = (k2_gained_points + k2_lost_points) / 2
                            

                            points = (k1_points + k2_points) / 2
                            
                            # print(id[0], points)
                            # print(k1_goal_home_sum, k1_goal_away_sum, k1_lost_home_sum, k1_lost_away_sum, goal_k1_home, goal_k1_away, lost_k1_home, lost_k1_away)
                            # print(k2_goal_home_sum, k2_goal_away_sum, k2_lost_home_sum, k2_lost_away_sum, goal_k2_home, goal_k2_away, lost_k2_home, lost_k2_away)
                            # print(k1_gained_points, k1_lost_points)
                            # print(k2_gained_points, k2_lost_points)
                            # print(k1_points, k2_points)
                            # print(points)


                            if float(points) > coefficient:
                                link = f"https://www.flashscorekz.com/match/{id[0]}/#/match-summary"
                                name = id[1] + " - " + id[2]
                                
                                date_str = id[3].strftime('%d.%m.%Y')
                                time_str = id[3].strftime('%H:%M')
                                
                                # Стилизация ссылки
                                match_link = f'<a href="{link}" target="_blank" style="color: #007bff; text-decoration: none; transition: all 0.3s; font-weight: 500;">{name}</a>'
                                
                                # Стилизация рейтинга
                                rating_color = "#28a745" if float(points) > 1.5 else "#dc3545"
                                rating_badge = f'<span style="background-color: {rating_color}; color: white; padding: 3px 8px; border-radius: 4px;">{round(points, 1)}</span>'

                                if datetime.now() <= id[3]:
                                    table_data_list.append([
                                        put_html(f'<div style="min-width: 100px; white-space: nowrap;">{date_str}</div>'),
                                        put_html(f'<div style="min-width: 100px; white-space: nowrap;">{time_str}</div>'),
                                        put_html(f'<div style="color: #6c757d; font-style: italic;">{id[4]}</div>'),
                                        put_html(match_link),
                                        put_html(rating_badge)
                                    ])

                    if table_data_list:
                        with use_scope('scope1', clear=True):
                            # Создаем таблицу с inline-стилями
                            put_table(
                                table_data_list,
                                header=[
                                    put_html('<div style="background-color: #009879; color: white; padding: 12px 15px; text-align: left; position: sticky; top: 0;">Дата</div>'),
                                    put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">Время</div>'),
                                    put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">Лига</div>'),
                                    put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">Матч</div>'),
                                    put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">Индекс</div>')
                                ]
                                ).style(
                                    'width: 100%; '
                                    'border-collapse: collapse; '
                                    'margin: 1rem 0; '
                                    'box-shadow: 0 0 20px rgba(0, 0, 0, 0.1); '
                                    'font-family: Arial, sans-serif;'
                                )
                            
                            # Добавляем скрипт для hover-эффектов
                            run_js('''
                                Array.from(document.querySelectorAll("tr")).forEach(row => {
                                    row.style.borderBottom = "1px solid #dddddd";
                                    row.style.background = (row.rowIndex % 2 === 0) ? "#f8f9fa" : "white";
                                    row.onmouseover = () => row.style.background = "#f1f1f1";
                                    row.onmouseout = () => row.style.background = (row.rowIndex % 2 === 0) ? "#f8f9fa" : "white";
                                });
                            ''')
                    else:
                        with use_scope('scope1', clear=True):
                            put_error("🚨 Нет данных по указанным параметрам!").style(
                                'padding: 15px; '
                                'background-color: #ffeef0; '
                                'color: #dc3545; '
                                'border: 1px solid #dc3545; '
                                'border-radius: 6px; '
                                'margin: 20px 0; '
                                'font-weight: bold;'
                            )

                    actions(buttons=[{"label": "Новый запрос", "value": "new", "color": "success"}])
                    clear_scope('scope1')
            except SessionClosedException:
                break
if __name__ == '__main__':
    smart_monitor()
