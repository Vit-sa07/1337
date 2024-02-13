from django.db import models
from django.conf import settings


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    title = models.CharField('Заголовок', max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    content = models.TextField('Содержание')
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def __str__(self):
        return self.title


class Response(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='responses', on_delete=models.CASCADE, verbose_name='Запрос')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    content = models.TextField('Содержание')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f'Ответ на {self.ticket.title}'
