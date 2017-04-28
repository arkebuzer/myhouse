from django.test import TestCase

from meteo.models import Meteo
from utils.enums import TimePointEnum


class MeteoModelTests(TestCase):

    def test_str(self):
        meteo = Meteo(temperature=21.97, pressure=743.24, humidity=29)
        self.assertEqual(str(meteo), '21.97 ℃, 743.24 mmHg, 29 %')


class TimePointEnumTests(TestCase):
    def test_str(self):
        self.assertEqual(str(TimePointEnum.HOUR), 'HOUR')
        self.assertNotEqual(str(TimePointEnum.MONTH), 'hour')

    def test_equals_to_str(self):
        self.assertTrue(TimePointEnum.HOUR.equals_to_str('HOUR'))
        self.assertTrue(TimePointEnum.DAY.equals_to_str('day'))
        self.assertTrue(TimePointEnum.MONTH.equals_to_str('mOnTh'))
        self.assertFalse(TimePointEnum.HOUR.equals_to_str('MONTH'))
