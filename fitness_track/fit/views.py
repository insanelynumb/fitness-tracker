from datetime import timedelta, datetime
from django.db.models import Avg, Count
from django.forms import DateInput
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from fit.forms import WeightLogForm, NewFoodForm, ExistFoodForm, UserRegistrationForm
from fit.models import weight_log, Food, ExerciseLog, Exercise
from django.contrib import messages
from django.utils import timezone
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from fit.forms import forms
import io
import urllib, base64
import matplotlib.pyplot as plt
import json, os, matplotlib
import numpy as np

def button_class(active_exercise, button):
    if active_exercise == button:
        return 'btn btn-outline-secondary btn-sm active'
    else:
        return 'btn btn-outline-secondary btn-sm'

@login_required()
def home(request):
    return render(request, 'home.html')


def logweight(request):
    if not request.user.is_authenticated:
        return redirect('fit:login')
    else:
        context = {
            'title': 'Weight Log',
            'weight_logs': weight_log.objects.filter(user=request.user).order_by('-timestamp'),
            'savedWeight': False
        }

        if request.method == 'POST':
            form = WeightLogForm(request.POST)
            if form.is_valid():
                w = weight_log(weight=form.cleaned_data['weight'], user=request.user)
                w.save()
                context['savedWeight'] = True
        else:
            form = WeightLogForm()

        context['form'] = form

        return render(request, 'logweight.html', context)

def foodrecord(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        # Handling form submissions
        if request.method == 'POST' and 'sub_btn_1' in request.POST:
            form_sub = NewFoodForm(request.POST)
            if form_sub.is_valid():
                # Ensuring calories match description if already in database
                val = True
                if Food.objects.filter(user=request.user, description=form_sub.cleaned_data['description']).exists():
                    old_entry = Food.objects.filter(user=request.user, description=form_sub.cleaned_data['description']).first()
                    if old_entry.calories != form_sub.cleaned_data['calories']:
                        messages.error(request, "ERROR: Reused descriptions must match calories!", extra_tags='danger')
                        val = False
                    else:
                        f = Food(date=form_sub.cleaned_data['date'], description=form_sub.cleaned_data['description'], calories=form_sub.cleaned_data['calories'], user=request.user)
                        f.save()
                # Ensuring calories are 0 or greater
                if form_sub.cleaned_data['calories'] < 0:
                    messages.error(request, "ERROR: Calories must be greater or equal to 0!", extra_tags='danger')
                    val = False
                if val == True:
                    f = Food(date=form_sub.cleaned_data['date'], description=form_sub.cleaned_data['description'], calories=form_sub.cleaned_data['calories'], user=request.user)
                    f.save()
                    messages.success(request, "Successfully added " + form_sub.cleaned_data['description'] + ".", extra_tags='success')
            else:
                messages.error(request, "ERROR: Description may only contain alphanumerics, end stops, commas, and parentheses!", extra_tags='danger')
        elif request.method == 'POST' and 'sub_btn_2' in request.POST:
            form_sub = ExistFoodForm(request.POST, request=request)
            if form_sub.is_valid():
                f = Food.objects.filter(user=request.user, description=form_sub.cleaned_data['description']).first()
                f.pk = None
                f.date = form_sub.cleaned_data["date"]
                f.save()
                messages.success(request, "Successfully added " + form_sub.cleaned_data['description'] + ".", extra_tags='success')
        elif request.method == 'POST':
            f = Food.objects.filter(user=request.user, pk=request.POST['pk']).first()
            Food.objects.filter(user=request.user, pk=request.POST['pk']).delete()
            messages.success(request, "Successfully deleted " + f.description + ".", extra_tags='success')
        # Creating forms
        form = NewFoodForm()
        form_2 = ExistFoodForm(request=request)

        # Getting data
        entries = Food.objects.filter(user=request.user).order_by('-date')
        data = {}
        for e in entries:
            if e.date in data:
                data[e.date].append(e)
            else:
                data[e.date] = [e]
        total_calories = {}
        for date in data:
            sum = 0
            for foods in data[date]:
                sum = sum + foods.calories
            total_calories[date] = sum

        # Passing info
        context = {
            'title': 'Food Record',
            'data': data,
            'form': form,
            'form_2': form_2,
            'total_calories': total_calories,
            'today_date': timezone.now().date(),
            'yesterday_date': timezone.now().date() - timedelta(days=1)
        }
        return render(request, 'foodrecord.html', context)

def exercises(request, active_exercises=0):

    if not request.user.is_authenticated:
        return redirect('login')
    else:
        classes = {
            'button1_class': button_class(active_exercises, 102),
            'button2_class': button_class(active_exercises, 106),
            'button3_class': button_class(active_exercises, 103),
            'button4_class': button_class(active_exercises, 110),
            'button5_class': button_class(active_exercises, 111),
            'button6_class': button_class(active_exercises, 112),
            'button7_class': button_class(active_exercises, 113),
            'button8_class': button_class(active_exercises, 114),
            'button9_class': button_class(active_exercises, 117),
            'button10_class': button_class(active_exercises, 118),
            'button11_class': button_class(active_exercises, 120),
            'button12_class': button_class(active_exercises, 121),
            'button13_class': button_class(active_exercises, 119),
            'button14_class': button_class(active_exercises, 101),
            'button15_class': button_class(active_exercises, 104),
        }

        exercise_list = []

        with open(os.path.dirname(os.path.realpath(__file__)) + '/Exercises.json') as f:
            data = json.load(f)

        if (active_exercises == 100):
            exercise_list = data
        else:
            for item in data:
                if item["group_code"] == active_exercises:
                    exercise_list.append(item)

        context = {
            'exercises': exercise_list,
            'title': 'Exercises',
            'active_exercise': active_exercises,
            'classes': classes,
        }
        return render(request, 'exercises.html', context)

def exhome(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        context = {
            'exercise_logs' : ExerciseLog.objects.filter(user=request.user.id).order_by('-date', '-id'),
            'exercises' : Exercise.objects.all(),
            'title' : 'Exercise Log',
            'user_id' : request.user.id,
        }
        if not context['exercise_logs'].count():
            return render(request, 'get_started.html')

        return render(request, 'exhome.html', context)

class ExlogDetailView(DetailView):
    model = ExerciseLog
    context_object_name = "exlog"
    template_name = 'ExerciseLog_Detail.html'

    # Getting extra context for the class-based view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # The line below literally took me hours to figure out
        context['exercises'] = Exercise.objects.filter(exercise_log=self.object).iterator()
        return context

class ExlogCreateView(LoginRequiredMixin, CreateView):
    model = ExerciseLog
    fields = ['date']
    template_name = 'ExerciseLog_Form.html'

    def get_form(self):
        form = super(ExlogCreateView, self).get_form()
        initial_base = self.get_initial()
        initial_base['date'] = timezone.now()
        form.initial = initial_base
        form.fields['date'].widget = DateInput()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Workout Log successfully added!", extra_tags='success')
        return super().form_valid(form)


class ExlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ExerciseLog
    fields = ['date']
    template_name = 'ExerciseLog_Form.html'
    def get_form(self):
        form = super(ExlogUpdateView, self).get_form()
        initial_base = self.get_initial()
        initial_base['date'] = timezone.now()
        form.initial = initial_base
        form.fields['date'].widget = DateInput()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Workout Log successfully updated!", extra_tags='success')
        return super().form_valid(form)

    # Test to see if current logged in user is the creator of the workout log
    def test_func(self):
        exlog = self.get_object()
        if self.request.user == exlog.user:
            return True
        return False


# Class based view for Delete (Exercise Log)
class ExlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ExerciseLog
    context_object_name = "exlog"
    success_url = '/fit/exhome/'
    template_name = 'exerciselog_confirm_delete.html'

    def test_func(self):
        exlog = self.get_object()
        if self.request.user == exlog.user:

            if self.request.method == 'POST':
                messages.success(self.request, "Workout Log successfully removed!", extra_tags='success')
            return True
        return False


class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    fields = ['exercise_name', 'num_sets', 'num_reps', 'exercise_weight']
    template_name = 'Exercise_Form.html'
    def form_valid(self, form):
        form.instance.exercise_log = ExerciseLog.objects.get(id=self.kwargs['pk'])
        messages.success(self.request, "Exercise successfully added!", extra_tags='success')
        return super().form_valid(form)

class ExerciseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Exercise
    fields = ['num_sets', 'num_reps', 'exercise_weight']
    template_name = 'Exercise_Form.html'
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Exercise successfully updated!", extra_tags='success')
        return super().form_valid(form)

    def test_func(self):
        exlog = self.get_object()
        if self.request.user == exlog.exercise_log.user:
            return True
        return False

class ExerciseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Exercise
    template_name = 'exercise_delete.html'
    success_url = reverse_lazy('fit:exlog_home')
    def test_func(self):
        exlog = self.get_object()
        if self.request.user == exlog.exercise_log.user:
            if self.request.method == 'POST':
                messages.success(self.request, "Exercise successfully removed!", extra_tags='success')
            return True
        return False


def add_from_recommender(request, exercise_name):
    today_log = None

    try:
        today_log = ExerciseLog.objects.get(user=request.user, date=datetime.date.today())
    except ExerciseLog.DoesNotExist:
        # If it doesn't exist, create a new one
        today_log = ExerciseLog.objects.create(
            user=request.user,
            date=datetime.date.today(),
        )

    # Create the exercise
    Exercise.objects.create(
        exercise_log=today_log,
        exercise_name=exercise_name,
        num_sets=0,
        num_reps=0,
        exercise_weight=0,
    )

    messages.success(request, "Exercise successfully added to today's workout log!!", extra_tags='success')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class DateInput(forms.DateInput):
    input_type = 'date'

def results(request):

    if not request.user.is_authenticated:
        return redirect('app:login')
    else:
        # Weight Plot
        matplotlib.use('Agg')
        plt.close()
        plt.plot([str(i.timestamp.date().day) + '/' + str(i.timestamp.date().month) for i in
                  weight_log.objects.filter(user=request.user).order_by('timestamp')],
                 [int(i.weight) for i in weight_log.objects.filter(user=request.user).order_by('timestamp')],
                 marker='o', markersize=5, color='blue')
        plt.xlabel('Date')
        plt.ylabel('Weight (lbs)')

        for i in range(0, len(weight_log.objects.filter(user=request.user))):
            plt.annotate(int(weight_log.objects.filter(user=request.user)[i].weight),
                         (str(weight_log.objects.filter(user=request.user)[i].timestamp.date().day) + '/' + str(
                             weight_log.objects.filter(user=request.user)[i].timestamp.date().month),
                          int(weight_log.objects.filter(user=request.user)[i].weight) + 2),
                         ha="center")
        fig1 = plt.gcf()
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format='png')
        buf1.seek(0)
        string = base64.b64encode(buf1.read())
        img1 = urllib.parse.quote(string)
        plt.close()

        list = Food.objects.filter(user=request.user).order_by('date').extra({'_date': 'Date(date)'}).values(
             '_date').annotate(val=Avg('calories'), count=Count('calories'))

        dates = []
        cals = []
        counts = []
        avgCals = 0
        for item in list:
            print(item)
            date = item.get('_date')
            date = date.split('-')
            dates.append(date[1] + '-' + date[2])
            cals.append(item.get('val'))
            counts.append(item.get('count'))
            avgCals = avgCals + item.get('val') * item.get('count')
        if len(dates) > 0:
            avgCals = avgCals / len(dates)

        # Calorie Plot
        plt.plot([i for i in dates],
                 [int(j * counts[i]) for i,j in enumerate(cals)],
                 marker='o', markersize=5, color='blue')
        plt.xlabel('Date')
        plt.ylabel('Calories Consumed')
        fig2 = plt.gcf()

        for i in range(0, len(dates)):
            plt.annotate(int(cals[i] * counts[i]), (dates[i], cals[i] * counts[i] +2), ha="center")

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format='png')
        buf2.seek(0)
        string = base64.b64encode(buf2.read())
        img2 = urllib.parse.quote(string)
        plt.close()

        ex_names = []
        for i in ExerciseLog.objects.filter(user=request.user):
            for j in Exercise.objects.filter(exercise_log=i):
                ex_names.append(j.exercise_name)

        weights = []
        reps = []
        dates = []
        rep_max = []
        for i in ExerciseLog.objects.filter(user=request.user).order_by('date'):
            for j in Exercise.objects.filter(exercise_log=i):
                if j.exercise_name == request.GET.get('ex', ''):
                    weights.append(j.exercise_weight)
                    reps.append(j.num_reps)
                    dates.append(i.date)

                    # Epley formula for 1RM calculation
                    rep_max.append(int(j.exercise_weight * (1 + j.num_reps / 30)))

        # Strength Plot
        plt.plot([str(i) for i in dates], rep_max, marker='o', markersize=5, color='blue')
        plt.title(request.GET.get('ex', 'Select an exercise'))
        plt.xlabel('Date')
        plt.ylabel(request.GET.get('ex', '') + ' (1 Repetition Maximum)')

        if len(rep_max) > 0:
            plt.ylim(min(rep_max) - 10, max(rep_max) + 10)

        for i in range(0, len(dates)):
            plt.annotate(int(rep_max[i]), (str(dates[i]), rep_max[i] + 2), ha="center")

        fig3 = plt.gcf()
        buf3 = io.BytesIO()
        fig3.savefig(buf3, format='png')
        buf3.seek(0)
        string = base64.b64encode(buf3.read())
        img3 = urllib.parse.quote(string)
        plt.close()

        weightSum = 0
        for i in weight_log.objects.filter(user=request.user):
            weightSum += int(i.weight)

        if len(weight_log.objects.filter(user=request.user)) > 0:
            average = weightSum / (len(weight_log.objects.filter(user=request.user)))
            average = '%.2f' % average
            change = int(weight_log.objects.filter(user=request.user)[len(weight_log.objects.filter(user=request.user)) - 1].weight) - int(weight_log.objects.filter(user=request.user)[0].weight)
        else:
            average = '--'
            change = '--'

        if len(rep_max) > 0:
            if (rep_max[0] != 0):
                str_change = ((rep_max[len(rep_max) - 1] - rep_max[0]) / rep_max[0]) * 100
                str_change = '%.2f' % str_change
            else:
                str_change = "Inf"
        else:
            str_change = '--'

        print(cals)
        context = {
            'title': 'Results',
            'img1': img1,
            'img2': img2,
            'img3': img3,
            'change': change,
            'average': average,
            'ex_names': np.unique(np.array(ex_names)),
            'str_change': str_change,
            'avg_cals': avgCals
        }
        return render(request, 'results.html', context)

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        else:
            form = UserRegistrationForm()

        context = {
            'title': 'Sign Up',
            'form': form
        }
        return render(request, 'signup.html', context)
