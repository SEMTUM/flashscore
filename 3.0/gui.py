from pywebio.platform import config
from pywebio.input import input, DATE, actions, input_group
from pywebio.output import put_text, put_table, put_scrollable, use_scope, clear_scope, put_html, put_error
from main import FlashScore as fs
from datetime import datetime
from pywebio.session import run_js
from pywebio.exceptions import SessionClosedException
import logging
from logging import StreamHandler



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
    .markdown-body table td, .markdown-body table th {
        padding: 4px 0;
        border: 1px solid #dfe2e5;
    }
    #pywebio-scope-log_scope {
        height: 400px;
        overflow: auto;
        padding: 10px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        margin-top: 15px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    
    #pywebio-scope-log_scope::-webkit-scrollbar {
        width: 8px;
    }
    
    #pywebio-scope-log_scope::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    #pywebio-scope-log_scope::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    #pywebio-scope-log_scope::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
'''

config(title="FlashScore 3.0 (Баскетбол)", css_style=css)


class PyWebIOLogHandler(logging.Handler):
    def __init__(self, scope_name="log_scope"):
        super().__init__()
        self.scope_name = scope_name
        self.level_colors = {
            'INFO': '#3498db',
            'WARNING': '#f39c12',
            'ERROR': '#e74c3c',
            'CRITICAL': '#c0392b',
            'DEBUG': '#2ecc71'
        }

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        color = self.level_colors.get(level, '#95a5a6')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        with use_scope(self.scope_name, clear=False):
            put_html(f'''
                <div style="
                    margin: 5px 0;
                    padding: 8px 12px;
                    border-left: 4px solid {color};
                    background-color: #f8f9fa;
                    border-radius: 0 4px 4px 0;
                    font-family: monospace;
                    display: flex;
                    align-items: center;
                ">
                    <span style="
                        color: #7f8c8d;
                        margin-right: 10px;
                        font-size: 0.85em;
                        min-width: 70px;
                    ">{timestamp}</span>
                    <span style="
                        font-weight: bold;
                        color: {color};
                        margin-right: 8px;
                        min-width: 70px;
                    ">{level}</span>
                    <span style="color: #2c3e50;">{msg}</span>
                </div>
            ''')
            # Автопрокрутка вниз
            run_js(f'''
                var logScope = document.getElementById('pywebio-scope-{self.scope_name}');
                if (logScope) {{
                    logScope.scrollTop = logScope.scrollHeight;
                }}
            ''')


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
                            )
                        ]
                    )
                    search_date = datetime.strptime(data["date"], '%Y-%m-%d')
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

                        put_html('<div style="margin-top:20px; margin-bottom:20px; font-weight:500; color:#444">Журнал выполнения:</div>')
                        use_scope('log_scope')
                        

                        search_list = fs.get_basketball_matches_info(num)
                        for match in search_list:
                            status = True
                            link = f"https://www.flashscorekz.com/match/basketball/{match['match_id']}/#/match-summary"
                            name = match['team_1'] + " - " + match['team_2']
                            date_str = match['datetime'].strftime('%d.%m.%Y')
                            time_str = match['datetime'].strftime('%H:%M')

                            com_1_goal = int(match['k1_score'][1].split(':')[0]) / int(match['k1_score'][0])
                            com_1_lost = int(match['k1_score'][1].split(':')[1]) / int(match['k1_score'][0])
                            com_2_goal = int(match['k2_score'][1].split(':')[0]) / int(match['k2_score'][0])
                            com_2_lost = int(match['k2_score'][1].split(':')[1]) / int(match['k2_score'][0])

                            index_1 = int(com_1_goal + com_2_lost)
                            index_2 = int(com_2_goal + com_1_lost)

                            index_itogo = index_1 - index_2

                            com_1_goal_home = int(match['k1_score_home'][1].split(':')[0]) / int(match['k1_score_home'][0])
                            com_1_lost_home = int(match['k1_score_home'][1].split(':')[1]) / int(match['k1_score_home'][0])
                            com_2_goal_away = int(match['k2_score_away'][1].split(':')[0]) / int(match['k2_score_away'][0])
                            com_2_lost_away = int(match['k2_score_away'][1].split(':')[1]) / int(match['k2_score_away'][0])
                            
                            index_3 = int(com_1_goal_home + com_2_lost_away)
                            index_4 = int(com_2_goal_away + com_1_lost_home)

                            index_d_g = index_3 - index_4
                            
                            index = (index_itogo + index_d_g) / 2

                            if index < 0:
                                prognoz = 'K2'
                            elif index > 0:
                                prognoz = 'K1'
                            else:
                                prognoz = None

                            if (index_itogo <=0 and index_d_g > 0) or (index_d_g <=0 and index_itogo > 0):
                                status = False

                                    
                            # Стилизация ссылки
                            match_link = f'<a href="{link}" target="_blank" style="color: #007bff; text-decoration: none; transition: all 0.3s; font-weight: 500; margin: 0 8px;">{name}</a>'

                            if datetime.now() <= match['datetime'] and prognoz != None and status == True:
                                table_data_list.append([
                                    put_html(f'<div style="min-width: 100px; white-space: nowrap; text-align: center;">{date_str}</div>'),
                                    put_html(f'<div style="min-width: 100px; white-space: nowrap; text-align: center;">{time_str}</div>'),
                                    put_html(f'<div style="color: #6c757d; font-style: italic;  margin: 0 8px;">{match['league']}</div>'),
                                    put_html(match_link),
                                    put_html(f'<div style="min-width: 100px; white-space: nowrap; text-align: center;">{match['k_1']}</div>'),
                                    put_html(f'<div style="min-width: 100px; white-space: nowrap; text-align: center;">{match['k_2']}</div>'),
                                    put_html(f'<div style="min-width: 100px; white-space: nowrap; text-align: center;">{index}</div>'),
                                    put_html(f'<div style="min-width: 100px; white-space: nowrap; text-align: center;">{prognoz}</div>')
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
                                            put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">К1</div>'),
                                            put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">К2</div>'),
                                            put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">Индекс</div>'),
                                            put_html('<div style="background-color: #009879; color: white; padding: 12px 15px;">Прогноз</div>')
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
    # Настройка обработчика логов
    logger = logging.getLogger('__main__')  # Получаем корневой логгер
    handler = PyWebIOLogHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    smart_monitor()
