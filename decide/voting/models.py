from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

from base import mods
from base.models import Auth, Key
from postproc.models import PostProcType


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)

    # Leave empty if it doesn't apply.
    TYPE_CHOICES = [(PostProcType.IDENTITY, "Identity"), (PostProcType.WEIGHT, "Weight"),
                    (PostProcType.SEATS, "Seats"), (PostProcType.PARITY, "Parity"), (PostProcType.TEAM, "Team")]
    postproc_type = models.IntegerField(blank=True, null=True, choices=TYPE_CHOICES, default=PostProcType.IDENTITY)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [[i['a'], i['b']] for i in votes]

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data, response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data, response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        questions = self.questions.all()

        qsts = []
        for qst in questions:
            opts = []
            for opt in qst.options.all():
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes,
                    'gender': opt.gender,
                    'team': opt.team,
                    'weight': opt.weight,
                })
            qsts.append({'number': qst.number, 'options': opts, 'seats': qst.seats})

        data = { 'type': self.postproc_type, 'questions': qsts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name


class Question(models.Model):
    voting = models.ForeignKey(Voting, null=True, related_name='questions', on_delete = models.CASCADE)
    # Automatic assignment for the question number on save
    number = models.PositiveIntegerField(editable = False, null = True)
    desc = models.TextField()
    help_text = models.TextField(max_length = 300, blank = True, null = True)

    yes_no_choices = ((True, 'Yes'), (False, 'No'))
    yes_no_question = models.BooleanField(default=False,verbose_name="Yes/No question", help_text="Check the box to generate automatically the options yes/no ")

    #choices=yes_no_choices
    
    def save(self):
        # Automatic assignment for the question number
        if not self.number:
            questions = self.voting.questions.all()
            if questions:
                self.number = questions.last().number + 1
            else:
                self.number = 1
    
        return super().save()
            
    # Leave empty if it doesn't apply.
    seats = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.desc, self.number)


@receiver(post_save, sender=Question)
def check_question(sender, instance, **kwargs):
    if instance.yes_no_question==True and instance.options.all().count()==0:
        op1 = QuestionOption(question=instance, number=1, option="Si")
        op1.save()
        op2 = QuestionOption(question=instance, number=2, option="No") 
        op2.save()


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    # Automatic assignment for the option number on save
    number = models.PositiveIntegerField(editable = False, null = True)
    option = models.TextField()

    # Leave empty if it doesn't apply.
    weight = models.IntegerField(blank=True, null=True)

    # Leave empty if it doesn't apply.
    BOOL_CHOICES = ((True, 'Male'), (False, 'Female'))
    gender = models.NullBooleanField(blank=True, null=True, choices=BOOL_CHOICES)

    # Leave empty if it doesn't apply.
    team = models.IntegerField(blank=True, null=True)
    
    def save(self):
        # Automatic assignment for the question number
        if not self.number:
            number = 0
            questions = self.question.voting.questions.all()
            for q in questions:
                options = q.options.all()
                for op in options:
                    if op.number and number < op.number:
                        number = op.number
            self.number = number + 1
        return super().save()
    
    def __str__(self):
        return '{} ({})'.format(self.option, self.number)
