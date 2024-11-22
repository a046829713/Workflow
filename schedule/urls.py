from django.urls import re_path
from django.views.generic.list import ListView

from schedule.feeds import CalendarICalendar, UpcomingEventsFeed
from schedule.models import Calendar
from schedule.periods import Day, Month, Week, Year
from schedule.views import (
    CalendarByPeriodsView,
    CalendarView,
    CancelOccurrenceView,
    CreateEventView,
    CreateOccurrenceView,
    DeleteEventView,
    EditEventView,
    EditOccurrenceView,
    EventView,
    FullCalendarView,
    OccurrencePreview,
    OccurrenceView,
    UpdateVisitorView,
    DeleteVisitorView,
    VisitorListView,
    CreateVisitorEventView,
    api_move_or_resize_by_code,
    api_occurrences,
    api_select_create,
    api_ask_form_todo_time
)

from schedule.othersviews import (
    GuardRoomView
)
urlpatterns = [
    # 可以瀏覽所有的首頁
    re_path(r"^$", ListView.as_view(model=Calendar), name="calendar_list"),


    # 各個行事曆的詳細內容
    re_path(
        r"^fullcalendar/(?P<calendar_slug>[-\w]+)/$",
        FullCalendarView.as_view(),
        name="fullcalendar",
    ),

    re_path(
        r"^calendar/year/(?P<calendar_slug>[-\w]+)/$",
        CalendarByPeriodsView.as_view(
            template_name="schedule/calendar_year.html"),
        name="year_calendar",
        kwargs={"period": Year},
    ),
    re_path(
        r"^calendar/tri_month/(?P<calendar_slug>[-\w]+)/$",
        CalendarByPeriodsView.as_view(
            template_name="schedule/calendar_tri_month.html"),
        name="tri_month_calendar",
        kwargs={"period": Month},
    ),
    re_path(
        r"^calendar/compact_month/(?P<calendar_slug>[-\w]+)/$",
        CalendarByPeriodsView.as_view(
            template_name="schedule/calendar_compact_month.html"
        ),
        name="compact_calendar",
        kwargs={"period": Month},
    ),
    re_path(
        r"^calendar/month/(?P<calendar_slug>[-\w]+)/$",
        CalendarByPeriodsView.as_view(
            template_name="schedule/calendar_month.html"),
        name="month_calendar",
        kwargs={"period": Month},
    ),
    re_path(
        r"^calendar/week/(?P<calendar_slug>[-\w]+)/$",
        CalendarByPeriodsView.as_view(
            template_name="schedule/calendar_week.html"),
        name="week_calendar",
        kwargs={"period": Week},
    ),
    re_path(
        r"^calendar/daily/(?P<calendar_slug>[-\w]+)/$",
        CalendarByPeriodsView.as_view(
            template_name="schedule/calendar_day.html"),
        name="day_calendar",
        kwargs={"period": Day},
    ),
    re_path(
        r"^calendar/(?P<calendar_slug>[-\w]+)/$",
        CalendarView.as_view(),
        name="calendar_home",
    ),

    # Event Urls
    re_path(
        r"^event/create/(?P<calendar_slug>[-\w]+)/$",
        CreateEventView.as_view(),
        name="calendar_create_event",
    ),


    # Visitor Event Urls
    re_path(
        r"^event/create/VendorVisitScheduler",
        CreateVisitorEventView.as_view(),
        name="create_visitor_event",
    ),


    re_path(
        r"^visitor_event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        CreateVisitorEventView.as_view(),
        name="edit_visitor_event",
    ),

    re_path(
        r"^event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$",
        EditEventView.as_view(),
        name="edit_event",
    ),
    
    re_path(
        r"^guardroom",
        GuardRoomView.as_view(),
        name="guardroom",
    ),





    #
    re_path(
        r"^Visitor/update/(?P<pk>\d+)",
        UpdateVisitorView.as_view(),
        name="VisitorUpdate",
    ),

    re_path(r"^Visitor/delete/(?P<pk>\d+)",
            DeleteVisitorView.as_view(), name='visitor_delete'),

    re_path(r"^visitor_list", VisitorListView.as_view(), name="visitor_list"),




    # 可以讓使用者詳細閱讀裡面的資料 有編輯和刪除
    re_path(r"^event/(?P<event_id>\d+)/$", EventView.as_view(), name="event"),

    re_path(
        r"^event/delete/(?P<event_id>\d+)/$",
        DeleteEventView.as_view(),
        name="delete_event",
    ),
    # urls for already persisted occurrences
    re_path(
        r"^occurrence/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$",
        OccurrenceView.as_view(),
        name="occurrence",
    ),
    re_path(
        r"^occurrence/cancel/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$",
        CancelOccurrenceView.as_view(),
        name="cancel_occurrence",
    ),
    re_path(
        r"^occurrence/edit/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$",
        EditOccurrenceView.as_view(),
        name="edit_occurrence",
    ),
    # urls for unpersisted occurrences
    re_path(
        r"^occurrence/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$",
        OccurrencePreview.as_view(),
        name="occurrence_by_date",
    ),
    re_path(
        r"^occurrence/cancel/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$",
        CancelOccurrenceView.as_view(),
        name="cancel_occurrence_by_date",
    ),
    re_path(
        r"^occurrence/edit/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$",
        CreateOccurrenceView.as_view(),
        name="edit_occurrence_by_date",
    ),
    # feed urls
    re_path(
        r"^feed/calendar/upcoming/(?P<calendar_id>\d+)/$",
        UpcomingEventsFeed(),
        name="upcoming_events_feed",
    ),
    re_path(r"^ical/calendar/(.*)/$",
            CalendarICalendar(), name="calendar_ical"),

    # api urls
    re_path(r"^api/occurrences", api_occurrences, name="api_occurrences"),

    re_path(
        r"^api/move_or_resize/$", api_move_or_resize_by_code, name="api_move_or_resize"
    ),
    re_path(r"^api/select_create/$", api_select_create,
            name="api_select_create"),

    re_path(r"^api/ask_form_todo_time/$", api_ask_form_todo_time,
            name="api_ask_form_todo_time"),


    re_path(r"^$", ListView.as_view(
        queryset=Calendar.objects.all()), name="schedule"),
]
