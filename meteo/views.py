from datetime import timedelta

from django.db.models import Avg
from django.db.models.functions import TruncHour, TruncMinute, TruncDay
from django.shortcuts import render
from django.utils import timezone

import pygal
from pygal.style import Style

from meteo.models import Meteo
from utils.dbfunctions import Round
from utils.enums import TimePointEnum


def index(request, time_delta='day'):
    meteo_data, time_format = get_meteo_data(time_delta)

    temperature_chart = get_chart_data_uri(meteo_data,
                                           time_format,
                                           data_key='temperature',
                                           data_label='Температура',
                                           y_range=(15, 35),
                                           x_label_key='time_point')

    pressure_chart = get_chart_data_uri(meteo_data,
                                        time_format,
                                        data_key='pressure',
                                        data_label='Давление',
                                        y_range=(730, 760),
                                        x_label_key='time_point',
                                        color='saddleBrown')

    humidity_chart = get_chart_data_uri(meteo_data,
                                        time_format,
                                        data_key='humidity',
                                        data_label='Влажность',
                                        y_range=(20, 90),
                                        x_label_key='time_point',
                                        color='blue')

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


def get_meteo_data(time_delta):
    """Returns meteo data and time_format for specified time_delta."""

    if TimePointEnum.MONTH.equals_to_str(time_delta):
        point_ago = timezone.localtime(timezone.now())
        point_ago = point_ago.replace(
            year=point_ago.year if point_ago.month > 1 else point_ago.year - 1,
            month=point_ago.month - 1 if point_ago.month > 1 else 12
        )

        cur_sub_point = timezone.localtime(timezone.now()).day
        time_format = '%d.%m.%Y'

        # Last month data grouped by day.
        meteo_data = Meteo.objects.filter(processed_dttm__gte=point_ago) \
            .exclude(processed_dttm__day=cur_sub_point) \
            .values(time_point=TruncDay('processed_dttm')) \
            .annotate(temperature=Round(Avg('temperature'), 2),
                      pressure=Round(Avg('pressure'), 2),
                      humidity=Round(Avg('humidity'), 0)) \
            .order_by('time_point')

    elif TimePointEnum.DAY.equals_to_str(time_delta):
        point_ago = timezone.localtime(timezone.now()) - timedelta(days=1)
        cur_sub_point = timezone.localtime(timezone.now()).hour
        time_format = '%d.%m - %H:00'

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


def get_chart_data_uri(meteo_data,
                       time_format,
                       data_key,
                       data_label,
                       y_range,
                       x_label_key,
                       x_label_rotation=45,
                       color='red'):
    style = Style(colors=(color,),
                  tooltip_font_size=18,
                  label_font_size=14,
                  major_label_font_size=14,
                  legend_font_size=16)

    chart = pygal.Line(range=y_range,
                       x_label_rotation=x_label_rotation,
                       style=style,
                       x_labels_major_every=2,
                       show_minor_x_labels=False)
    chart.x_labels = [d[x_label_key].strftime(time_format) for d in meteo_data]
    chart.add(data_label, [d[data_key] for d in meteo_data])
    return chart.render_data_uri()
