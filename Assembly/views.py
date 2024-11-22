from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from workFlow.Custom import GroupRequiredMixin
from django.views.generic import View
from .forms import QualityAbnormalApplicationForm
from workFlow import Appsettings
from workFlow.DataTransformer import querydict_to_dict, GetFormID
from Company.DataTransformer import create_form_and_save, handle_process, check_and_save_file
from django.shortcuts import render, redirect
from Company.models import Form

# Create your views here.



    