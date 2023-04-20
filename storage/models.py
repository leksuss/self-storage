from django.db import models

class User(models.Model):

    tg_username = models.CharField(
        verbose_name='Никнейм в мессенджере',
        null=True, blank=True,
    )
    chat_id = models.IntegerField(
        verbose_name='ID чата',
        null=True, blank=True,
    )
    phone = models.CharField(
        verbose_name='Телефон',
        null=True, blank=True,
    )
    address = models.TextField(
        verbose_name='Адрес',
        null=True, blank=True,
    )
    utm_source = models.CharField(
        verbose_name='Откуда пришел',
        null=True, blank=True,
    )

    def __str__(self):
        return self.tg_username

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'Клиенты'


class Box(models.Model):

    user_id = models.ForeignKey(User,
        verbose_name='Клиент',
        null=True, blank=True,
        on_delete=models.CASCADE,
    )
    size = models.IntegerField(
        verbose_name='Размеры',
        null=True, blank=True,
    )
    volume = models.IntegerField(
        verbose_name='Объем',
        null=True, blank=True,
    )
    paid_from = models.DateTimeField(
        verbose_name='Оплачено с',
        null=True, blank=True,
    )
    paid_till = models.DateTimeField(
        verbose_name='Оплачено по',
        null=True, blank=True,
    )
    description = models.TextField(
        verbose_name='Откуда пришел',
        null=True, blank=True,
    )

    def __str__(self):
        return f'{self.user_id.tg_username} с {self.paid_from} по {self.paid_till}'

    class Meta:
        verbose_name = 'бокс'
        verbose_name_plural = 'Боксы'


class TransferRequest(models.Model):

    TRANSFER_TYPE = (
        (0, 'Забор груза'),
        (1, 'Доставка груза'),
    )

    box_id = models.ForeignKey(Box,
        verbose_name='Бокс',
        null=True, blank=True,
        on_delete=models.CASCADE,
    )

    transfer_type = models.CharField(
        verbose_name='Тип трансфера',
        choices = TRANSFER_TYPE
    )

    address = models.TextField(
        verbose_name='Адрес забора/доставки',
        null=True, blank=True,
    )
    time_arrive = models.DateTimeField(
        verbose_name='Желаемое время',
        null=True, blank=True,
    )
    is_complete = models.BooleanField(
        verbose_name='Исполнено?',
        null=True, blank=True,
    )
    is_call_needed = models.BooleanField(
        verbose_name='Нужен ли обратный звонок',
        null=True, blank=True,
    )

    def __str__(self):
        return f'{self.transfer_type} в {self.time_arrive}'

    class Meta:
        verbose_name = 'трансфер'
        verbose_name_plural = 'Трансферы'


class Promocodes(models.Model):

    name = models.CharField(
        verbose_name='Название',
        null=True, blank=True,
    )

    discount = models.IntegerField(
        verbose_name='Скидка в %',
        null=True, blank=True,
    )

    valid_till = models.DateTimeField(
        verbose_name='До какой даты работает',
        null=True, blank=True,
    )

    def __str__(self):
        return f'{self.name}, скидка {self.discount}'

    class Meta:
        verbose_name = 'промокод'
        verbose_name_plural = 'Промокоды'