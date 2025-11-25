from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("cookie-policy/", views.CookiePolicyView.as_view(), name="cookie_policy"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("terms/", views.TermsView.as_view(), name="terms"),

]