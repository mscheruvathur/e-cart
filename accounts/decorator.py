
from django.shortcuts import redirect,render

def admin_decorator(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.session.has_key('is_logged') == False:
            return render(request,'admin_panel_templates/login.html')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func