import datetime
from urllib.parse import quote

import dateutil.parser
import pytz
from django.conf import settings
from django.db.models import F, Q
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

try:
    from django.utils.http import url_has_allowed_host_and_scheme
except ImportError:
    # Django<=2.2
    from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme

from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    ModelFormMixin,
    ProcessFormView,
    UpdateView,
)

from schedule.forms import EventForm, OccurrenceForm, VisitForm, EventVisitForm
from schedule.models import Calendar, Event, Occurrence, Visitor
from schedule.periods import weekday_names
from schedule.settings import (
    CHECK_EVENT_PERM_FUNC,
    CHECK_OCCURRENCE_PERM_FUNC,
    EVENT_NAME_PLACEHOLDER,
    GET_EVENTS_FUNC,
    OCCURRENCE_CANCEL_REDIRECT,
    USE_FULLCALENDAR,
)
from schedule.utils import (
    check_calendar_permissions,
    check_event_permissions,
    check_occurrence_permissions,
    coerce_date_dict,
    convert_str_datetime,
    convert_to_minutes
)

from workFlow.Debug_tool import Check_input_output
from Company.models import Form
import json
from workFlow.Appsettings import EXPERIMENTALTEST_MAP
from django.shortcuts import render
from Database import SQL_operate
from Company.models import CustomUser, Employee
from django.views.generic import ListView
import time
from django.urls import reverse_lazy

# views.py
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from schedule.models import Event, Occurrence, Visitor
from django.utils.decorators import method_decorator


class CalendarViewPermissionMixin:
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return check_calendar_permissions(view)


class EventEditPermissionMixin:
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return check_event_permissions(view)


class OccurrenceEditPermissionMixin:
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return check_occurrence_permissions(view)


class CancelButtonMixin:
    def post(self, request, *args, **kwargs):
        next_url = kwargs.get("next")
        self.success_url = get_next_url(request, next_url)
        if "cancel" in request.POST:
            return HttpResponseRedirect(self.success_url)
        else:
            return super().post(request, *args, **kwargs)


class CalendarMixin(CalendarViewPermissionMixin):
    model = Calendar
    slug_url_kwarg = "calendar_slug"


class CalendarView(CalendarMixin, DetailView):
    template_name = "schedule/calendar.html"
    


class FullCalendarView(CalendarMixin, DetailView):
    template_name = "schedule/fullcalendar.html"
    login_url = '/login/'  # 指定这个视图特定的登录URL

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["calendar_slug"] = self.kwargs.get("calendar_slug")

        if context["calendar_slug"] == 'VendorVisitScheduler':
            context["add_event_url"] = reverse('create_visitor_event')
            print(context["add_event_url"])
        else:
            context["add_event_url"] = reverse('calendar_create_event', kwargs={
                                               'calendar_slug': context["calendar_slug"]})

        return context


class CalendarByPeriodsView(CalendarMixin, DetailView):
    template_name = "schedule/calendar_by_period.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = self.object
        period_class = self.kwargs["period"]
        try:
            date = coerce_date_dict(self.request.GET)
        except ValueError:
            raise Http404
        if date:
            try:
                date = datetime.datetime(**date)
            except ValueError:
                raise Http404
        else:
            date = timezone.now()
        event_list = GET_EVENTS_FUNC(self.request, calendar)

        local_timezone = timezone.get_current_timezone()
        period = period_class(event_list, date, tzinfo=local_timezone)

        context.update(
            {
                "date": date,
                "period": period,
                "calendar": calendar,
                "weekday_names": weekday_names,
                "here": quote(self.request.get_full_path()),
            }
        )
        return context


class OccurrenceMixin(CalendarViewPermissionMixin, TemplateResponseMixin):
    model = Occurrence
    pk_url_kwarg = "occurrence_id"
    form_class = OccurrenceForm


class OccurrenceEditMixin(
    CancelButtonMixin, OccurrenceEditPermissionMixin, OccurrenceMixin
):
    def get_initial(self):
        initial_data = super().get_initial()
        _, self.object = get_occurrence(**self.kwargs)
        return initial_data


class OccurrenceView(OccurrenceMixin, DetailView):
    template_name = "schedule/occurrence.html"


class OccurrencePreview(OccurrenceMixin, ModelFormMixin, ProcessFormView):
    template_name = "schedule/occurrence.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = {"event": self.object.event, "occurrence": self.object}
        return context


class EditOccurrenceView(OccurrenceEditMixin, UpdateView):
    template_name = "schedule/edit_occurrence.html"


class CreateOccurrenceView(OccurrenceEditMixin, CreateView):
    template_name = "schedule/edit_occurrence.html"


class CancelOccurrenceView(OccurrenceEditMixin, ModelFormMixin, ProcessFormView):
    template_name = "schedule/cancel_occurrence.html"

    def post(self, request, *args, **kwargs):
        event, occurrence = get_occurrence(**kwargs)
        self.success_url = kwargs.get(
            "next", get_next_url(request, event.get_absolute_url())
        )
        if "cancel" not in request.POST:
            occurrence.cancel()
        return HttpResponseRedirect(self.success_url)


class EventMixin(CalendarViewPermissionMixin):
    model = Event
    pk_url_kwarg = "event_id"


class EventEditMixin(CancelButtonMixin, EventEditPermissionMixin, EventMixin):
    pass


class EventView(EventMixin, DetailView):
    template_name = "schedule/event.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        _slug = Calendar.objects.get(id=context['object'].calendar_id).slug
        if _slug == 'VendorVisitScheduler':
            this_event_visitor_id = context['object'].form_without_view.split(
                '-')[0]
            db = context['object'].form_without_view.split('-')[1]

            if db == 'schedule_visitor':
                visitor = Visitor.objects.get(id=this_event_visitor_id)

                _filter_user = CustomUser.objects.filter(
                    FullName=visitor.interviewee_name)

                filter_employee = Employee.objects.filter(worker_id__in=list(
                    _filter_user.values_list('username', flat=True)))

                context['visitor'] = visitor
                context['users'] = _filter_user
                # 需要知道單位
                context['unit'] = {
                    _each_object.worker_id: _each_object.unit for _each_object in filter_employee}

        return context


class EditEventView(EventEditMixin, UpdateView):
    template_name = "schedule/create_event.html"

    def get_form_class(self):
        # 根據具體情況返回不同的 form class
        if self.kwargs["calendar_slug"] == 'VendorVisitScheduler':
            return EventVisitForm
        else:
            return EventForm

    def _get_form_without_view(self):
        visitor_models = self.request.user.created_visitors.all()
        return [(str(model.id) + '-' + model.slug, str(model)) for model in visitor_models]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendar_slug'] = (self.kwargs["calendar_slug"])

        if self.kwargs["calendar_slug"] == 'VendorVisitScheduler':
            context['form'].fields['form_without_view'].choices = self._get_form_without_view()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if kwargs["calendar_slug"] == 'VendorVisitScheduler':
            form_without_view = request.POST.get('form_without_view', '')
            form.fields['form_without_view'].choices = [
                (form_without_view, form_without_view)]

        # Check if the form is valid
        if form.is_valid():
            return self.form_valid(form)
        else:
            # 如果表單無效，則重新設置選項並返回表單錯誤
            form.fields['form_without_view'].choices = self._get_form_without_view()
            return self.form_invalid(form)

    def form_valid(self, form):
        event = form.save(commit=False)
        old_event = Event.objects.get(pk=event.pk)
        dts = datetime.timedelta(
            minutes=int((event.start - old_event.start).total_seconds() / 60)
        )
        dte = datetime.timedelta(
            minutes=int((event.end - old_event.end).total_seconds() / 60)
        )
        event.occurrence_set.all().update(
            original_start=F("original_start") + dts,
            original_end=F("original_end") + dte,
        )
        event.save()
        return super().form_valid(form)


class UpdateVisitorView(UpdateView):
    model = Visitor  # 这里指定你的模型
    form_class = VisitForm
    template_name = "schedule/visitor.html"
    login_url = '/login/'  # 指定这个视图特定的登录URL
    success_url = reverse_lazy('visitor_list')  # 删除成功后重定向的URL

    def _get_factno_na(self):
        FACT_df = SQL_operate.DB_operate(sqltype='YBIT').get_pd_data(
            'select FACT_NO,FACT_NA from FACT')

        ouput = []
        for i in range(FACT_df.shape[0]):
            FACT_NO = FACT_df.iloc[i]['FACT_NO']
            FACT_NA = FACT_df.iloc[i]['FACT_NA']
            ouput.append((FACT_NO, FACT_NO + ' ' + FACT_NA))

        return ouput

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 當使用者的所選擇的公司是自己打的時候，或是其他部門有打過的時候
        this_factno_na = self._get_factno_na()

        new_factno = [
            _each_visitor
            for _each_visitor in set(Visitor.objects.values_list('company_id', flat=True))
            if _each_visitor not in {fact[0] for fact in this_factno_na}
        ]
        new_factno = [(_factno, _factno) for _factno in new_factno]

        context['form'].fields['company_id'].choices = this_factno_na + new_factno
        context['form'].fields['tellphone_number'].choices = [
            (_, _) for _ in json.loads(context['object'].tellphone_number.replace("'", '"'))]
        return context

    def checkifexist(self, company_id: str, corporation_info: list):
        return any(company_id == company[0] for company in corporation_info)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        form = self.get_form()

        # 手动绑定实例到表单
        form.instance = instance

        # 檢查使用者輸入的公司行號是否為本公司已經有的公司
        company_id = request.POST.get('company_id', '')
        corporation_info = self._get_factno_na()

        if not self.checkifexist(company_id, corporation_info):
            form.fields['company_id'].choices = [(company_id, company_id)]
        else:
            form.fields['company_id'].choices = self._get_factno_na()

        form.fields['tellphone_number'].choices = [
            (_phone_numebr, _phone_numebr) for _phone_numebr in request.POST.getlist('tellphone_number')]
        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)  # 新增此行來打印錯誤信息
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        # 可以直接從表單控制變成控制model
        visitor = form.save(commit=False)

        # 先將之前的名稱清除掉，重新由ID來判斷
        visitor.company_name = ''

        for each_company in self._get_factno_na():
            if visitor.company_id == each_company[0]:
                visitor.company_name = each_company[1].split(' ')[1]
                break

        # 如果迭代完之後發現還是沒有
        if not visitor.company_name:
            visitor.company_name = visitor.company_id

        visitor.creator = self.request.user
        visitor.slug = 'schedule_visitor'  # 怕將來有多組標籤會用到 所以將DB也算傳入

        visitor.save()
        return super().form_valid(form)  # 使用默认的 form_valid 实现


class DeleteVisitorView(DeleteView):
    model = Visitor
    success_url = reverse_lazy('visitor_list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()  # 删除对象
        return HttpResponseRedirect(self.get_success_url())  # 重定向到 success_url


class DeleteEventView(EventEditMixin, DeleteView):
    template_name = "schedule/delete_event.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["next"] = self.get_success_url()
        return ctx

    def get_success_url(self):
        """
            After the event is deleted there are three options for redirect, tried in
            this order:
            # Try to find a 'next' GET variable
            # If the key word argument redirect is set
            # Lastly redirect to the event detail of the recently create event
        """
        url_val = "fullcalendar"
        next_url = self.kwargs.get("next") or reverse(
            url_val, args=[self.object.calendar.slug]
        )

        next_url = get_next_url(self.request, next_url)
        return next_url


class VisitorListView(ListView):
    model = Visitor
    template_name = "schedule/visitor_list.html"
    context_object_name = "visitors"  # 在模板中使用的上下文对象的名称
    paginate_by = 10  # 每页显示的对象数量

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 你可以在这里添加额外的上下文数据

        full_name_map = {str(obeject.id): obeject.FullName for obeject in (
            CustomUser.objects.all())}
        for _each_visitor in context['object_list']:
            full_names = []
            for _each_id in json.loads(_each_visitor.interviewee_name.replace("'", '"')):
                full_names.append(full_name_map[_each_id])

            _each_visitor.interviewee_name = full_names

        return context

    def get_queryset(self):
        # 我只要創建人是自己才顯示
        queryset = super().get_queryset()
        queryset = queryset.filter(creator=self.request.user)
        # 在这里添加任何过滤或排序
        return queryset


def get_occurrence(
    event_id,
    occurrence_id=None,
    year=None,
    month=None,
    day=None,
    hour=None,
    minute=None,
    second=None,
    tzinfo=None,
):
    """
    Because occurrences don't have to be persisted, there must be two ways to
    retrieve them. both need an event, but if its persisted the occurrence can
    be retrieved with an id. If it is not persisted it takes a date to
    retrieve it.  This function returns an event and occurrence regardless of
    which method is used.
    """
    if occurrence_id:
        occurrence = get_object_or_404(Occurrence, id=occurrence_id)
        event = occurrence.event
    elif None not in (year, month, day, hour, minute, second):
        event = get_object_or_404(Event, id=event_id)
        date = timezone.make_aware(
            datetime.datetime(
                int(year), int(month), int(day), int(
                    hour), int(minute), int(second)
            ),
            tzinfo,
        )
        occurrence = event.get_occurrence(date)
        if occurrence is None:
            raise Http404
    else:
        raise Http404
    return event, occurrence


def check_next_url(next_url):
    """
    Checks to make sure the next url is not redirecting to another page.
    Basically it is a minimal security check.
    """
    if not next_url or "://" in next_url:
        return None
    return next_url


def get_next_url(request, default):
    next_url = default
    if OCCURRENCE_CANCEL_REDIRECT:
        next_url = OCCURRENCE_CANCEL_REDIRECT
    _next_url = (
        request.GET.get("next")
        if request.method in ["GET", "HEAD"]
        else request.POST.get("next")
    )
    if _next_url and url_has_allowed_host_and_scheme(_next_url, request.get_host()):
        next_url = _next_url
    return next_url


def determine_date_to_keep(datetime_input):
    # If the time is exactly midnight, return only the date, otherwise return the full datetime
    if datetime_input.time() == datetime.datetime.min.time():
        return datetime_input.date()
    else:
        return datetime_input


@check_calendar_permissions
def api_occurrences(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    calendar_slug = request.GET.get("calendar_slug")
    timezone = request.GET.get("timeZone")
    try:
        response_data = _api_occurrences(start, end, calendar_slug, timezone)
    except (ValueError, Calendar.DoesNotExist) as e:
        return HttpResponseBadRequest(e)

    return JsonResponse(response_data, safe=False)


def _get_title(occurrence, calendar_slug):
    if calendar_slug == 'VendorVisitScheduler':
        id, databaseslug = occurrence.event.form_without_view.split('-')
        # 判斷是否為相同的資料庫
        if databaseslug == 'schedule_visitor':
            int_id = int(id)
            visitor = Visitor.objects.get(id=int_id)

        outstr = visitor.company_name + '-' + \
            occurrence.title if visitor.company_name else occurrence.title
        outstr = outstr + '-' + visitor.interviewee_name
    else:
        outstr = occurrence.event.form_id + '-' + \
            occurrence.title if occurrence.event.form_id else occurrence.title

    return outstr


def _api_occurrences(start, end, calendar_slug, timezone):
    # 如果不給時區的話就會是 2024-04-28T00:00:00+08:00
    if not start or not end:
        raise ValueError("Start and end parameters are required")

    start = convert_str_datetime(start)
    end = convert_str_datetime(end)

    current_tz = False
    if timezone and timezone in pytz.common_timezones:
        # make start and end dates aware in given timezone
        current_tz = pytz.timezone(timezone)
        start = current_tz.localize(start)
        end = current_tz.localize(end)

    elif settings.USE_TZ:
        # If USE_TZ is True, make start and end dates aware in UTC timezone
        utc = pytz.UTC
        start = utc.localize(start)
        end = utc.localize(end)

    if calendar_slug:
        # will raise DoesNotExist exception if no match
        calendars = [Calendar.objects.get(slug=calendar_slug)]
    # if no calendar slug is given, get all the calendars
    else:
        calendars = Calendar.objects.all()

    response_data = []
    # Algorithm to get an id for the occurrences in fullcalendar (NOT THE SAME
    # AS IN THE DB) which are always unique.
    # Fullcalendar thinks that all their "events" with the same "event.id" in
    # their system are the same object, because it's not really built around
    # the idea of events (generators)
    # and occurrences (their events).
    # Check the "persisted" boolean value that tells it whether to change the
    # event, using the "event_id" or the occurrence with the specified "id".
    # for more info https://github.com/llazzaro/django-scheduler/pull/169
    i = 1
    if Occurrence.objects.all().exists():
        i = Occurrence.objects.latest("id").id + 1

    event_list = []
    for calendar in calendars:
        # create flat list of events from each calendar
        event_list += calendar.events.filter(start__lte=end).filter(
            Q(end_recurring_period__gte=start) | Q(
                end_recurring_period__isnull=True)
        )

    for event in event_list:
        occurrences = event.get_occurrences(start, end)
        for occurrence in occurrences:
            occurrence_id = i + occurrence.event.id
            existed = False

            if occurrence.id:
                occurrence_id = occurrence.id
                existed = True

            recur_rule = occurrence.event.rule.name if occurrence.event.rule else None

            if occurrence.event.end_recurring_period:
                recur_period_end = occurrence.event.end_recurring_period
                if current_tz:
                    # make recur_period_end aware in given timezone
                    recur_period_end = recur_period_end.astimezone(current_tz)
                recur_period_end = recur_period_end
            else:
                recur_period_end = None

            event_start = occurrence.start
            event_end = occurrence.end

            if current_tz:
                # make event start and end dates aware in given timezone
                event_start = event_start.astimezone(current_tz)
                event_end = event_end.astimezone(current_tz)

            if occurrence.cancelled:
                # fixes bug 508
                continue

            response_data.append(
                {
                    "id": occurrence_id,
                    "title": _get_title(occurrence, calendar_slug),
                    "start": determine_date_to_keep(event_start),
                    "end": determine_date_to_keep(event_end),
                    "existed": existed,
                    "event_id": occurrence.event.id,
                    "color": occurrence.event.color_event,
                    "description": occurrence.description,
                    "rule": recur_rule,
                    "end_recurring_period": recur_period_end,
                    "creator": str(occurrence.event.creator),
                    "calendar": occurrence.event.calendar.slug,
                    "cancelled": occurrence.cancelled,
                }
            )

    return response_data


@require_POST
@check_calendar_permissions
def api_move_or_resize_by_code(request):
    response_data = {}
    user = request.user
    id = request.POST.get("id")
    existed = bool(request.POST.get("existed") == "true")
    # V3 version
    # delta = datetime.timedelta(minutes=int(request.POST.get("delta")))

    # V6 version
    delta = datetime.timedelta(minutes=convert_to_minutes(
        json.loads(request.POST.get("delta"))))

    resize = bool(request.POST.get("resize", False))
    event_id = request.POST.get("event_id")

    response_data = _api_move_or_resize_by_code(
        user, id, existed, delta, resize, event_id
    )
    return JsonResponse(response_data)


@Check_input_output
def _api_move_or_resize_by_code(user, id, existed, delta, resize, event_id):
    response_data = {}
    response_data["status"] = "PERMISSION DENIED"
    if existed:
        occurrence = Occurrence.objects.get(id=id)
        occurrence.end += delta
        if not resize:
            occurrence.start += delta
        if CHECK_OCCURRENCE_PERM_FUNC(occurrence, user):
            occurrence.save()
            response_data["status"] = "OK"
    else:
        event = Event.objects.get(id=event_id)
        dts = 0
        dte = delta
        if not resize:
            event.start += delta
            dts = delta
        event.end = event.end + delta
        if CHECK_EVENT_PERM_FUNC(event, user):
            event.save()

            # occurrence 的作用是甚麼暫時不知道
            # event.occurrence_set.all().update(
            #     original_start=F("original_start") + dts,
            #     original_end=F("original_end") + dte,
            # )
            response_data["status"] = "OK"

    return response_data


@require_POST
@check_calendar_permissions
def api_select_create(request):
    response_data = {}
    start = request.POST.get("start")
    end = request.POST.get("end")
    calendar_slug = request.POST.get("calendar_slug")

    response_data = _api_select_create(start, end, calendar_slug)

    return JsonResponse(response_data)


def _api_select_create(start, end, calendar_slug):
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)

    calendar = Calendar.objects.get(slug=calendar_slug)
    Event.objects.create(
        start=start, end=end, title=EVENT_NAME_PLACEHOLDER, calendar=calendar
    )

    response_data = {}
    response_data["status"] = "OK"
    return response_data


def calculate_business_days(start_time, usetime):
    # 用來判斷是否足夠實驗室的時間，要排除工作天
    count_days = 0
    current_date = datetime.datetime.strptime(
        start_time, "%Y-%m-%d %H:%M").date()

    while count_days < int(usetime):
        # 檢查下一天是否為工作日
        current_date += datetime.timedelta(days=1)
        if 0 <= current_date.weekday() <= 4:  # 週一到週五
            count_days += 1

    return current_date


def api_ask_form_todo_time(request):
    user_chose_id = request.POST.get("user_chose_id")
    start_time = request.POST.get("start_time")
    form = Form.objects.get(form_id=user_chose_id)

    # 獲得實驗室所需要的時間
    usetime = EXPERIMENTALTEST_MAP[form.data['test_type']]
    finally_date = calculate_business_days(start_time, usetime)
    response_data = {}
    response_data["status"] = "OK"
    response_data["finally_date"] = finally_date
    return JsonResponse(response_data)


class CreateVisitorEventView(SessionWizardView):
    """
        創造編輯可以一起使用
    """
    template_name = "schedule/create_visitor_event.html"
    login_url = '/login/'  # 指定这个视图特定的登录URL
    success_url = reverse_lazy('fullcalendar', kwargs={
                               'calendar_slug': 'VendorVisitScheduler'})  # 修正 success_url
    form_list = [
        ('step1', VisitForm),
        ('step2', EventForm),
    ]

    def dispatch(self, request, *args, **kwargs):
        self.event_id = kwargs.get('event_id')
        if self.event_id:
            visitor_id = Event.objects.get(
                # type:ignore
                id=self.event_id).form_without_view.split('-')[0]
            self.visitor_instance = get_object_or_404(Visitor, id=visitor_id)
            self.event_instance = get_object_or_404(Event, id=self.event_id)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        date = request.GET.get("date")
        if date:
            request.session['date'] = date

        return super().get(request, *args, **kwargs)
        
        
    def get_form_kwargs(self, step=None):
        """
        為每個步驟的表單傳遞額外的參數，這裡是當前用戶。
        """
        kwargs = super().get_form_kwargs(step)
        kwargs['user'] = self.request.user

        if self.event_id:
            if step == 'step1':
                # 提供現有的 Visitor 實例
                kwargs['instance'] = self.visitor_instance
            elif step == 'step2':
                kwargs['instance'] = self.event_instance

            
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["calendar_slug"] = 'VendorVisitScheduler'
        if 'date' in self.request.session and not self.event_id:
            context['start_time'] = self.request.session['date'] + " 00:00"            
        else:        
            form = self.get_form()
            # 取得未綁定的資料
            data = form.initial
            
            if data.get('start'):
                context['start_time'] = data.get('start')
            if data.get('end'):
                context['end_time'] = data.get('end')        
        return context

    def done(self, form_list, **kwargs):
        # 獲取每個表單的資料
        step1_data = self.get_cleaned_data_for_step('step1')
        step2_data = self.get_cleaned_data_for_step('step2')

        if self.event_id:
            # 編輯現有的對象
            visitor_instance = self.visitor_instance
            for attr, value in step1_data.items():  # type:ignore
                setattr(visitor_instance, attr, value)

            visitor_instance.save()

            event_instance = self.event_instance
            for attr, value in step2_data.items():  # type:ignore
                setattr(event_instance, attr, value)

            event_instance.save()
        else:
            # 获取每个表单的数据
            step1_data = self.get_cleaned_data_for_step('step1')
            step1_data['creator'] = self.request.user  # type:ignore
            
            step1_data['company_name'] = step1_data['company_id'] # type:ignore
            visitor_instance = Visitor.objects.create(
                **step1_data)  # type:ignore

            step2_data = self.get_cleaned_data_for_step('step2')
            step2_data['creator'] = self.request.user  # type:ignore
            step2_data['calendar'] = get_object_or_404( Calendar, slug='VendorVisitScheduler')  # type:ignore

            # form_without_view 用建立和表單之連結
            step2_data['form_without_view'] = str(visitor_instance.id) + "-schedule_visitor"  # type:ignore
            Event.objects.create(**step2_data)  # type:ignore
            # 處理所有步驟的資料
        
        # 清除 session 中的 date
        if 'date' in self.request.session:
            del self.request.session['date']
        
        return redirect(self.success_url)

    def post(self,request, *args, **kwargs):
        """
            In order to check out every step is ok.
        """
        current_step = self.steps.current
        form = self.get_form(data=self.request.POST)

        if form.is_valid():
            print(f"当前步骤 {current_step} 的表单验证通过")
            print(f"表单数据: {form.cleaned_data}")
        else:
            print(f"当前步骤 {current_step} 的表单验证失败")
            print(f"表单错误: {form.errors}")

        return super().post(request, *args, **kwargs)

class CreateEventView(EventEditMixin, CreateView):
    template_name = "schedule/create_event.html"
    login_url = '/login/'  # 指定这个视图特定的登录URL

    def get_form_class(self):
        # 根據具體情況返回不同的 form class
        if self.kwargs["calendar_slug"] == 'VendorVisitScheduler':
            return EventVisitForm
        else:
            return EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendar_slug'] = (self.kwargs["calendar_slug"])

        if self.kwargs["calendar_slug"] == 'VendorVisitScheduler':
            context['form'].fields['form_without_view'].choices = self._get_form_without_view()

        return context

    def post(self, request, *args, **kwargs):
        # 如果您查看 BaseCreateView 的 post 方法，您會發現它設定了 self.object=None。由於您要重寫該方法，因此需要在程式碼中新增該行。
        self.object = None
        form = self.get_form()

        # 檢查使用者輸入的公司行號是否為本公司已經有的公司
        form_without_view = request.POST.get('form_without_view', '')
        form.fields['form_without_view'].choices = [
            (form_without_view, form_without_view)]

        if form.is_valid():
            return self.form_valid(form)
        else:
            # 如果表單無效，則重新設置選項並返回表單錯誤
            form.fields['form_without_view'].choices = self._get_form_without_view()
            return self.form_invalid(form)

    def form_valid(self, form):
        # 如果表单验证成功，Django 将调用 form_valid 方法。
        event = form.save(commit=False)
        event.creator = self.request.user
        event.calendar = get_object_or_404(
            Calendar, slug=self.kwargs["calendar_slug"])
        event.save()
        return HttpResponseRedirect(event.get_absolute_url())