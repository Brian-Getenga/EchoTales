from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('blog/', include('blog.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('markdownx/', include('markdownx.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Blog Administration"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Welcome to Blog Administration"