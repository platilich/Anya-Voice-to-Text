from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import TelegramUser


@staff_member_required
def custom_admin(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action and user_id:
            try:
                user = TelegramUser.objects.get(user_id=user_id)
                if action == 'ban':
                    user.is_banned = True
                elif action == 'unban':
                    user.is_banned = False
                user.save()

                # if from htmx, we send only user_card.html
                if request.headers.get('HX-Request'):
                    return render(request, 'user_card.html', {'user': user})

            except Exception as e:
                print("Ошибка:", e)

    # get every 5s
    users = TelegramUser.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'users': users})