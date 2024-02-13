# models.py в приложении reviews

from django.db import models
from django.conf import settings
from productss.models import Product

# models.py в приложении reviews

from django.db import models
from django.conf import settings
from productss.models import Product


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField('Оценка', default=5)
    is_published = models.BooleanField('Опубликован', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def __str__(self):
        return f'Отзыв от {self.user.username} на {self.product.name}'

