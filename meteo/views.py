from enum import Enum

from django.shortcuts import render

from django.db.models import Avg
from utils.dbfunctions import Round

from django.db.models.functions import TruncHour, TruncMinute
from django.utils import timezone
from datetime import timedelta

from meteo.models import Meteo

import pygal
from pygal.style import Style


def index(request, time_delta='day'):
    meteo_data, time_format = get_meteo_data(time_delta)

    temperature_chart = pygal.Line(range=(15, 35), x_label_rotation=45)
    temperature_chart.x_labels = [d['time_point'].strftime(time_format) for d in meteo_data]
    temperature_chart.add('Температура', [d['temperature'] for d in meteo_data])
    temperature_chart = temperature_chart.render_data_uri()

    brown = Style(colors=('saddleBrown',))
    pressure_chart = pygal.Line(range=(730, 760), x_label_rotation=45, style=brown)
    pressure_chart.x_labels = [d['time_point'].strftime('%Y-%m-%d - %H:00') for d in meteo_data]
    pressure_chart.add('Давление', [d['pressure'] for d in meteo_data])
    pressure_chart = pressure_chart.render_data_uri()

    blue = Style(colors=('blue',))
    humidity_chart = pygal.Line(range=(20, 90), x_label_rotation=45, style=blue)
    humidity_chart.x_labels = [d['time_point'].strftime('%Y-%m-%d - %H:00') for d in meteo_data]
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


class TimePointEnum(Enum):
    MONTH = 'MONTH'
    DAY = 'DAY'
    HOUR = 'HOUR'

    def equals_to_str(self, string):
        """Case insensitive equality test."""
        return self.value == string.upper()

    def __str__(self):
        return self.value


def get_meteo_data(time_delta):
    """Returns meteo data and time_format for specified time_delta."""

    if TimePointEnum.MONTH.equals_to_str(time_delta):
        point_ago = timezone.localtime(timezone.now())
        point_ago = point_ago.replace(
            year=point_ago.year if point_ago.month > 1 else point_ago.year - 1,
            month=point_ago.month - 1 if point_ago.month > 1 else 12
        )

        cur_sub_point = timezone.localtime(timezone.now()).day
        time_format = '%Y-%m-%d'

        # Last month data grouped by day.
        meteo_data = Meteo.objects.filter(processed_dttm__gte=point_ago) \
            .exclude(processed_dttm__day=cur_sub_point) \
            .values(time_point=TruncHour('processed_dttm')) \
            .annotate(temperature=Round(Avg('temperature'), 2),
                      pressure=Round(Avg('pressure'), 2),
                      humidity=Round(Avg('humidity'), 0)) \
            .order_by('time_point')

    elif TimePointEnum.DAY.equals_to_str(time_delta):
        point_ago = timezone.localtime(timezone.now()) - timedelta(days=1)
        cur_sub_point = timezone.localtime(timezone.now()).hour
        time_format = '%m-%d - %H:00'

        # Last day data grouped by hour.
        meteo_data = Meteo.objects.filter(processed_dttm__gte=point_ago) \
            .exclude(processed_dttm__hour=cur_sub_point) \
            .values(time_point=TruncHour('processed_dttm')) \
            .annotate(temperature=Round(Avg('temperature'), 2),
                      pressure=Round(Avg('pressure'), 2),
                      humidity=Round(Avg('humidity'), 0)) \
            .order_by('time_point')

    elif TimePointEnum.HOUR.equals_to_str(time_delta):
        point_ago = timezone.localtime(timezone.now()) - timedelta(hours=1)
        cur_sub_point = timezone.localtime(timezone.now()).minute
        time_format = '%H:%M:%S'

        # Last hour data grouped by minute.
        meteo_data = Meteo.objects.filter(processed_dttm__gte=point_ago) \
            .exclude(processed_dttm__minute=cur_sub_point) \
            .values(time_point=TruncMinute('processed_dttm')) \
            .annotate(temperature=Round(Avg('temperature'), 2),
                      pressure=Round(Avg('pressure'), 2),
                      humidity=Round(Avg('humidity'), 0)) \
            .order_by('time_point')
    else:
        raise ValueError('Invalid time interval passed!')

    return meteo_data, time_format
