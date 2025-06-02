from django.urls import path, include

urlpatterns = [
    # ... 其它平台路由 ...
    path('multiplatform/', include('MultiplatformDataDashboardDataSource.urls')),
] 