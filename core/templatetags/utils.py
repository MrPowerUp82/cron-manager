from django import template

register = template.Library()

WEEK_DAY = {
    "0": "Domingo",
    "1": "Segunda",
    "2": "Terça",
    "3": "Quarta",
    "4": "Quinta",
    "5": "Sexta",
    "6": "Sábado",
    "*": "Todos os dias",
}

@register.filter
def cron_to_week_day(x: str)-> str:
    try:
        idx = x.split(' ')[4]
        return WEEK_DAY.get(idx, 'Invalid day')
    except:
        return 'Invalid day'