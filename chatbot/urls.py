from django.urls import path

from .views import chatbot_page, ChatbotView


app_name = "chatbot"


urlpatterns = [

    path(
        "",
        chatbot_page,
        name="chatbot-page"
    ),

    path(
        "chat/",
        ChatbotView.as_view(),
        name="chat"
    ),

]