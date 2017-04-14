from datetime import timedelta

import pygal
from django.shortcuts import render

from django.utils import timezone
from pygal.style import Style

from meteo.models import Meteo


def index(request):
    day_ago_dt = timezone.localtime(timezone.now()).replace() - timedelta(days=1)
    meteo_data = Meteo.objects.filter(processed_dttm__gte=day_ago_dt).order_by('processed_dttm')

    temperature_chart = pygal.Line(range=(15, 35), x_label_rotation=30)
    temperature_chart.x_labels = [d.processed_dttm.strftime('%H-%M-%S') for d in meteo_data]
    temperature_chart.add('Температура', [d.temperature for d in meteo_data])
    temperature_chart = temperature_chart.render_data_uri()

    brown = Style(colors=('saddleBrown',))
    pressure_chart = pygal.Line(range=(730, 760), x_label_rotation=20, style=brown)
    pressure_chart.x_labels = [d.processed_dttm.strftime('%H-%M-%S') for d in meteo_data]
    pressure_chart.add('Давление', [d.pressure for d in meteo_data])
    pressure_chart = pressure_chart.render_data_uri()

    blue = Style(colors=('blue',))
    humidity_chart = pygal.Line(range=(20, 90), x_label_rotation=20, style=blue)
    humidity_chart.x_labels = [d.processed_dttm.strftime('%H-%M-%S') for d in meteo_data]
    humidity_chart.add('Влажность', [d.humidity for d in meteo_data])
    humidity_chart = humidity_chart.render_data_uri()

    try:
        cur_meteo_data = Meteo.objects.order_by("-id")[0]
    except IndexError:
        cur_meteo_data = None

    context = {
        'temperature_chart': temperature_chart,
        'pressure_chart': pressure_chart,
        'humidity_chart': humidity_chart,
        'cur_meteo_data': cur_meteo_data,
    }
    return render(request, 'meteo/index.html', context)
