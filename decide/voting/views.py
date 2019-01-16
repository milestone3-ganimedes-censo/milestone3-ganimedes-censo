import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Question, QuestionOption, Voting
from .serializers import VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth
from postproc.models import PostProcType


class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', )

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'questions', 'question_opts', 'postproc_type']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        if(len(request.data.get('questions')) != len(request.data.get('question_opts'))):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        postproc_type = request.data.get('postproc_type')
        types = [PostProcType.IDENTITY, PostProcType.WEIGHT, PostProcType.SEATS, PostProcType.PARITY, PostProcType.TEAM]
        if postproc_type is not None and postproc_type not in types:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = Voting(name = request.data.get('name'), desc = request.data.get('desc'))
        voting.save()
        
        for question_number, question_desc in enumerate(request.data.get('questions')):
            
            question = Question(voting = voting, number = (question_number + 1), desc = question_desc)
            question.save()
            
            for option_number, option_option in enumerate(request.data.get('question_opts')[question_number]):
                option = QuestionOption(question = question, number = (option_number + 1), option = option_option)
                option.save()
        
        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        auth.save()
        
        voting.auths.add(auth)
        
        return Response({}, status=status.HTTP_201_CREATED)

class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)

def get_open_votings(request):
    
    """
    Method to get all open votings (all votings that have
    start date and dont have end date.
    """
    
    try:
        open_votings = Voting.objects.filter(start_date__isnull = False, end_date__isnull = True)
    except:
        open_votings = []
    
    return render(request, 'voting/openVotings.html',
                  context={'open_votings':open_votings})
