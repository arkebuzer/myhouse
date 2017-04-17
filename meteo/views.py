from django.shortcuts import render

from django.db.models import Avg
from utils.dbfunctions import Round

from django.db.models.functions import TruncHour
from django.utils import timezone
from datetime import timedelta

from meteo.models import Meteo

import pygal
from pygal.style import Style


def index(request):
    day_ago_dt = timezone.localtime(timezone.now()) - timedelta(days=1)
    cur_hour = timezone.localtime(timezone.now()).hour

    # Last 24 hour data grouped by hour.
    meteo_data = Meteo.objects.filter(processed_dttm__gte=day_ago_dt) \
        .exclude(processed_dttm__hour=cur_hour) \
        .values(date_hour=TruncHour('processed_dttm')) \
        .annotate(temperature=Round(Avg('temperature'), 2),
                  pressure=Round(Avg('pressure'), 2),
                  humidity=Round(Avg('humidity'), 0)) \
        .order_by('date_hour')

    temperature_chart = pygal.Line(range=(15, 35), x_label_rotation=30)
    temperature_chart.x_labels = [d['date_hour'].strftime('%Y-%m-%d - %H:00') for d in meteo_data]
    temperature_chart.add('Температура', [d['temperature'] for d in meteo_data])
    temperature_chart = temperature_chart.render_data_uri()

    brown = Style(colors=('saddleBrown',))
    pressure_chart = pygal.Line(range=(730, 760), x_label_rotation=20, style=brown)
    pressure_chart.x_labels = [d['date_hour'].strftime('%Y-%m-%d - %H:00') for d in meteo_data]
    pressure_chart.add('Давление', [d['pressure'] for d in meteo_data])
    pressure_chart = pressure_chart.render_data_uri()

    blue = Style(colors=('blue',))
    humidity_chart = pygal.Line(range=(20, 90), x_label_rotation=20, style=blue)
    humidity_chart.x_labels = [d['date_hour'].strftime('%Y-%m-%d - %H:00') for d in meteo_data]
    humidity_chart.add('Влажность', [d['humidity'] for d in meteo_data])
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
