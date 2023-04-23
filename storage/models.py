from django.db import models

class User(models.Model):

    tg_username = models.CharField(
        'Никнейм в мессенджере',
        max_length=100,
    )
    chat_id = models.IntegerField(
        'ID чата',
    )
    phone = models.CharField(
        'Телефон',
        max_length=10,
        null=True,
    )
    address = models.TextField(
        'Адрес',
        null=True,
    )
    utm_source = models.CharField(
        'Откуда пришел',
        max_length=100,
        null=True,
    )
    from_owner = models.BooleanField(
        'Представитель заказчика',
        null=True,
    )

    def __str__(self):
        return self.tg_username

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'Клиенты'


class Box(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name='Клиент',
        related_name='boxes',
        on_delete=models.CASCADE,
    )
    weight = models.IntegerField(
        'Вес',
        null=True,
    )
    volume = models.IntegerField(
        'Объем',
        null=True,
    )
    paid_from = models.DateTimeField(
        'Оплачено с',
        null=True,
    )
    paid_till = models.DateTimeField(
        'Оплачено по',
        null=True,
    )
    description = models.TextField(
        'Хранимые вещи',
        null=True,
    )

    def __str__(self):
        return f'{self.user.tg_username} с {self.paid_from} по {self.paid_till}'

    class Meta:
        verbose_name = 'бокс'
        verbose_name_plural = 'Боксы'


class TransferRequest(models.Model):

    TRANSFER_TYPE = (
        (0, 'Забор груза'),
        (1, 'Доставка груза'),
    )

    box = models.ForeignKey(
        Box,
        verbose_name='Бокс',
        related_name='transfers',
        on_delete=models.CASCADE,
    )

    transfer_type = models.IntegerField(
        'Тип трансфера',
        choices = TRANSFER_TYPE
    )

    address = models.TextField(
        'Адрес забора/доставки',
    )
    time_arrive = models.CharField(
        'Желаемое время',
        max_length=10,
        null=True,
    )
    is_complete = models.BooleanField(
        'Исполнено?',
        default=False,
    )

    def __str__(self):
        return f'{self.transfer_type} в {self.time_arrive}'

    class Meta:
        verbose_name = 'трансфер'
        verbose_name_plural = 'Трансферы'


class Promocodes(models.Model):

    name = models.CharField(
        'Название',
        max_length=100,
    )

    discount = models.IntegerField(
        'Скидка в %',
    )

    valid_from = models.DateTimeField(
        'С какой даты работает',
        null=True,
    )

    valid_till = models.DateTimeField(
        verbose_name='До какой даты работает',
        null=True,
    )

    def __str__(self):
        return f'{self.name}, скидка {self.discount}'

    class Meta:
        verbose_name = 'промокод'
        verbose_name_plural = 'Промокоды'