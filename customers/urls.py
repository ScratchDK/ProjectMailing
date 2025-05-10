import customers.views as views
from django.urls import path
from customers.apps import CustomersConfig

app_name = CustomersConfig.name

urlpatterns = [
    path("", views.MailingListView.as_view(), name="mailing_list"),
    path('mailing_detail/<int:id>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path("mailing_create/", views.MailingView.as_view(), name="mailing_create"),
    path("mailing_update/<int:id>/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing_delete/<int:id>/", views.MailingDeleteView.as_view(), name="mailing_delete"),

    path("statistics/", views.AttemptListView.as_view(), name="statistics"),

    path("letter_list/", views.LetterListView.as_view(), name="letter_list"),
    path("letter/", views.LetterView.as_view(), name="letter"),
    path("letter_update/<int:id>/", views.LetterUpdateView.as_view(), name="letter_update"),
    path("letter_delete/<int:id>/", views.LetterDeleteView.as_view(), name="letter_delete"),

    path("recipient_list/", views.RecipientListView.as_view(), name="recipient_list"),
    path("recipient/", views.RecipientView.as_view(), name="recipient"),
    path("recipient_update/<int:id>/", views.RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipient_delete/<int:id>/", views.RecipientDeleteView.as_view(), name="recipient_delete"),
]
