from django import template
from accounts.models import Notification

register = template.Library()

#제대로 연결되는지 체크!ㅇㅇ 본 거 지우는 것
@register.inclusion_tag('accounts/show_notifications.html', takes_context=True)
def show_notifications(context):
	request_user = context['request'].user
	notifications = Notification.objects.filter(to_user=request_user).exclude(user_has_seen=True).order_by('-date')
	return {'notifications': notifications}