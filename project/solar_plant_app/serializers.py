from datetime import datetime

from rest_framework import serializers

from .models import Plant, Datapoint


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ('id', 'name')


class DataPointListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        """ This method helps to create or update date

        Args:
            validated_data:

        Returns:

        """
        data_point_list = []
        for item in validated_data:
            data_point, created = Datapoint.objects.update_or_create(
                plant=item['plant'],
                timestamp=item['timestamp'],
                defaults=item
            )
            data_point_list.append(data_point)

        return data_point_list


class DataPointSerializer(serializers.ModelSerializer):
    plant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Datapoint
        list_serializer_class = DataPointListSerializer
        fields = ('id', 'plant', 'timestamp', 'energy_expected',
                  'energy_observed', 'irradiation_expected',
                  'irradiation_observed')

    @classmethod
    def map_plant_data_points(cls, plant, data_list):
        """ As the data we received is nested data that's why we need to
        map to our model

        Args:
            plant:
            data_list:

        Returns:

        """
        data_points = []
        for data in data_list:
            d = {
                'plant': plant,
                'timestamp': datetime.fromisoformat(data['datetime']),
                'energy_expected': data['expected']['energy'],
                'energy_observed': data['observed']['energy'],
                'irradiation_expected': data['expected']['irradiation'],
                'irradiation_observed': data['observed']['irradiation']
            }
            data_points.append(d)
        return data_points
