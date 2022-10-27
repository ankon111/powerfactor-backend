from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Plant


class TestSolarPlantApp(APITestCase):

    def create_solar_plant(self):
        solar_plant_data = {'name': 'my-plant'}
        response = self.client.post(reverse('plant'), solar_plant_data)
        return response

    def test_create_solar_plant(self):
        response = self.create_solar_plant()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_solar_plants(self):
        self.create_solar_plant()
        response = self.client.get(reverse('plant'))
        plant_list = Plant.objects.all()
        self.assertTrue(len(plant_list) == len(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPlantDataPointView(APITestCase):

    def create_solar_plant(self):
        solar_plant_data = {'name': 'my-plant'}
        response = self.client.post(reverse('plant'), solar_plant_data)
        return response

    def test_plant_data_point_valid_request(self):
        plant_response = self.create_solar_plant()
        params = {
            'plant-id': plant_response.data['id'],
            'from': '2022-10-25',
            'to': '2022-10-26',
        }
        response = self.client.get(reverse('data'), params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_plant_data_point_invalid_plant_id(self):
        plant_response = self.create_solar_plant()
        params = {
            'plant-id': plant_response.data['id'] + 1,
            'from': '2022-10-25',
            'to': '2022-10-26',
        }
        response = self.client.get(reverse('data'), params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['results'], 'Object with plant id does not exists')

    def test_plant_data_point_without_to_date(self):
        plant_response = self.create_solar_plant()
        params = {
            'plant-id': plant_response.data['id'],
            'from': '2022-10-25'
        }
        response = self.client.get(reverse('data'), params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['results'], 'Please provide plant_id, from and to values')

    def test_plant_data_point_invalid_date_format(self):
        plant_response = self.create_solar_plant()
        params = {
            'plant-id': plant_response.data['id'],
            'from': '26-10-2022',
            'to': '2022-10-25',
        }
        response = self.client.get(reverse('data'), params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['results'], 'Incorrect data format, should be YYYY-MM-DD')

    def test_plant_data_point_from_date_greater_than_to_date(self):
        plant_response = self.create_solar_plant()
        params = {
            'plant-id': plant_response.data['id'],
            'from': '2022-10-26',
            'to': '2022-10-25',
        }
        response = self.client.get(reverse('data'), params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['results'], 'From date can not be greater than to date')
