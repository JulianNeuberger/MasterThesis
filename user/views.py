from django.shortcuts import redirect, render_to_response, render
from django.template import RequestContext

from user.forms import UserForm, UserProfileForm


def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        upf = UserProfileForm(request.POST, prefix='userprofile')
        if uf.is_valid() * upf.is_valid():
            user = uf.save(commit=False)
            user.set_password(uf.cleaned_data['password'])
            user.save()
            userprofile = upf.save(commit=False)
            userprofile.user = user
            userprofile.save()
            return redirect('login')
    else:
        uf = UserForm(prefix='user')
        upf = UserProfileForm(prefix='userprofile')
    return render(request,
                  'register.html',
                  dict(userform=uf, userprofileform=upf))
