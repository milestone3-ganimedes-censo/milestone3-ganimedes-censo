from rest_framework import serializers
from .models import Census


class CensusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Census
        fields = '__all__'