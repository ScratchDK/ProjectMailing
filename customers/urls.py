import customers.views as views
from django.urls import path
from customers.apps import CustomersConfig

app_name = CustomersConfig.name

urlpatterns = [
    path("", views.MailingListView.as_view(), name="mailing_list"),
    path("letter_list/", views.LetterListView.as_view(), name="letter_list"),
    path("recipient_list/", views.RecipientListView.as_view(), name="recipient_list"),
    path("statistics/", views.AttemptListView.as_view(), name="statistics"),
    path('mailing_detail/<int:id>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path("mailing_create/", views.MailingView.as_view(), name="mailing_create"),
    path("letter/", views.LetterView.as_view(), name="letter"),
    path("recipient/", views.RecipientView.as_view(), name="recipient"),
    path("mailing_update/<int:id>/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("letter_update/<int:id>/", views.LetterUpdateView.as_view(), name="letter_update"),
    path("letter_delete/<int:id>/", views.LetterDeleteView.as_view(), name="letter_delete"),
]
