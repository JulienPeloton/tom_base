import json

from django.conf import settings
from guardian.shortcuts import get_objects_for_user
from rest_framework import serializers

from tom_observations.models import DynamicCadence, ObservationGroup, ObservationRecord


class DynamicCadenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicCadence
        fields = '__all__'

    def to_representation(self, value):
        return f'{value.cadence_strategy} with parameters {value.cadence_parameters}'


class ObservationGroupSerializer(serializers.ModelSerializer):
    dynamic_cadences = serializers.StringRelatedField(many=True, read_only=True, source='dynamiccadence_set')

    class Meta:
        model = ObservationGroup
        fields = '__all__'


class ObservationRecordSerializer(serializers.ModelSerializer):
    # TODO: display cadences with observation groups
    observation_groups = serializers.StringRelatedField(many=True, read_only=True, source='observationgroup_set')

    class Meta:
        model = ObservationRecord
        fields = '__all__'

    # def create(self, validated_data):

    #     observation_record = ObservationRecord.objects.create(**validated_data)

    #     return observation_record

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['parameters'] = json.loads(representation['parameters'])
        return representation


class ObservationRecordFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    # This PrimaryKeyRelatedField subclass is used to implement get_queryset based on the permissions of the user
    # submitting the request. The pattern was taken from this StackOverflow answer: https://stackoverflow.com/a/32683066

    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not (request and queryset):
            return None
        if settings.TARGET_PERMISSIONS_ONLY:
            return ObservationRecord.objects.all()
        else:
            return get_objects_for_user(request.user, 'tom_observations.change_observation')
