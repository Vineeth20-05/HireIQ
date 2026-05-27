from django.shortcuts import (
    render,
    redirect
)


def home(request):

    if request.user.is_authenticated:

        if request.user.role == "recruiter":

            return redirect(
                "/recruiter/dashboard/"
            )

        elif request.user.role == "candidate":

            return redirect(
                "/candidate/dashboard/"
            )

    return render(
        request,
        "home.html"
    )