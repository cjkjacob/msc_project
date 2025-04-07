from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('submit-effort', views.queue_effort),
    path('validator/pending-efforts', views.list_pending_efforts),
    path('validator/approve-effort/<int:effort_id>', views.approve_effort),
    path('validator/reject-effort/<int:effort_id>', views.reject_effort),
    path('validator/rejected-efforts', views.list_rejected_efforts),
    path('efforts', views.list_efforts),
    path('chain', views.get_chain),
    path('validate', views.validate_chain),
    path('register-wallet', views.register_wallet),
    path('register', views.register),
    path('connect-node', views.connect_node),
    path('receive-block', views.receive_block, name='receive_block'),
    path("sync-chain", views.sync_chain_view),
    path('user-info/<str:username>', views.user_info_view),
    path('user/me', views.user_me_view),
    path('peers', views.list_peers),
    path('health', views.health_check),
    path('block-height', views.block_height),
    path('validator/dashboard', views.validator_dashboard),
    path('user/tokens', views.user_token_history),
    path('user/profile', views.user_profile),
    path('login', TokenObtainPairView.as_view()),
    path('leaderboard', views.leaderboard_view),
    path('token/refresh', TokenRefreshView.as_view()),
    path('upload', views.upload_file),
]