from rest_framework import serializers

from .models import Vote


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    a = serializers.IntegerField()
    b = serializers.IntegerField()

    class Meta:
        model = Vote
        fields = ('voting_id', 'voter_id', 'a', 'b')

class VotingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vote
        fields = ('voting_id')

class VoterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vote
        fields = ('voter')