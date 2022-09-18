import json


def generate_keyboard(kb_type):
    gen_kb = {}
    gen_kb['one_time'] = False
    gen_kb['buttons'] = []
    if kb_type == 'Запуск':
        buttons = []
        but_dict = {'action': {'type': 'text', 'label': 'Начать'}, 'color': 'primary'}
        buttons.append(but_dict)
        gen_kb['buttons'].append(buttons)
    elif kb_type == 'Начать':
        buttons = []
        but_dict = {'action': {'type': 'text', 'label': 'Поиск'}, 'color': 'primary'}
        buttons.append(but_dict)
        gen_kb['buttons'].append(buttons)
    elif kb_type == 'Поиск':
        buttons = []
        but_dict = {'action': {'type': 'text', 'label': 'В избранное'}, 'color': 'secondary'}
        buttons.append(but_dict)
        but_dict = {'action': {'type': 'text', 'label': 'Следующий'}, 'color': 'secondary'}
        buttons.append(but_dict)
        but_dict = {'action': {'type': 'text', 'label': 'Завершить работу'}, 'color': 'negative'}
        buttons.append(but_dict)
        gen_kb['buttons'].append(buttons)
    elif kb_type == 'В избранное':
        buttons = []
        but_dict = {'action': {'type': 'text', 'label': 'В избранное'}, 'color': 'secondary'}
        buttons.append(but_dict)
        but_dict = {'action': {'type': 'text', 'label': 'Следующий'}, 'color': 'secondary'}
        buttons.append(but_dict)        
        but_dict = {'action': {'type': 'text', 'label': 'Показать избранное'}, 'color': 'secondary'}
        buttons.append(but_dict)
        but_dict = {'action': {'type': 'text', 'label': 'Завершить работу'}, 'color': 'negative'}
        buttons.append(but_dict)
        gen_kb['buttons'].append(buttons)
    elif kb_type == 'Показать избранное':
        buttons = []        
        but_dict = {'action': {'type': 'text', 'label': 'Поиск'}, 'color': 'primary'}
        buttons.append(but_dict)
        but_dict = {'action': {'type': 'text', 'label': 'Показать избранное'}, 'color': 'secondary'}
        buttons.append(but_dict)
        but_dict = {'action': {'type': 'text', 'label': 'Завершить работу'}, 'color': 'negative'}
        buttons.append(but_dict)
        gen_kb['buttons'].append(buttons)    

    jstr = json.dumps(gen_kb, indent=4)
    return jstr