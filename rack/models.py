from django.db import models
from django.urls import reverse


class Rack(models.Model):
	title = models.CharField('Название стойки', max_length=50)
	size = models.PositiveIntegerField('Размер', help_text='Размер измеряется в целых юнитах')
	space = models.JSONField('Пространство для серверов', null=True)
	note = models.TextField('Заметки', blank=True, null=True)
	reverse_side = models.ManyToManyField('self', verbose_name='Обратная сторона стойки')
	backside = models.BooleanField('Является задней стороной?', blank=True, null=True)

	class Meta:
		verbose_name = 'Стойка'
		verbose_name_plural = 'Стойки'

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('rack_detail', kwargs={'pk': self.pk})


class Port(models.Model):
	SPEED_CHOICES = [('10Mbit', '10Mbit'), ('100Mbit', '100Mbit'), ('1Gbit', '1Gbit'), ('10Gbit', '10Gbit')]
	MATERIAL_CHOICES = [('Медь', 'Медь'), ('Оптика', 'Оптика')]

	note = models.TextField('Комментарий', blank=True, null=True)
	color = models.CharField('Цвет', max_length=20)
	speed = models.CharField('Скорость порта', choices=SPEED_CHOICES, max_length=20)
	material = models.CharField('Тип порта', choices=MATERIAL_CHOICES, max_length=20)
	server = models.ForeignKey('Server', on_delete=models.CASCADE)
	connection = models.TextField('Подключён к', blank=True, null=True, help_text='Для создания связи используйте формат #id#номер_порта или #id#номер_порта#скорость, например: #123#1 или #123#1#1000')
	link = models.ManyToManyField('self', 'Связь с портом', through='LinkPort')
	number = models.PositiveIntegerField('Порядковый номер порта')

	class Meta:
		verbose_name = 'Порт'
		verbose_name_plural = 'Порты'

	def __str__(self):
		return f'{self.pk} - {self.speed}, {self.material}'


class Server(models.Model):
	title = models.CharField('Название', max_length=50)
	position = models.PositiveIntegerField('Позиция на сервере', default=0)
	length = models.PositiveIntegerField('Размер')
	note = models.TextField('Заметки', blank=True, null=True)
	rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, null=True)
	color = models.CharField('Цвет', max_length=50)
	base_speed = models.CharField('Скорость порта по умолчанию', choices=Port.SPEED_CHOICES, max_length=20)
	base_material = models.CharField('Тип порта по умолчанию', choices=Port.MATERIAL_CHOICES, max_length=20)

	class Meta:
		verbose_name = 'Сервер'
		verbose_name_plural = 'Серверы'

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('server_detail', kwargs={'pk': self.pk})


class LinkPort(models.Model):
	port1 = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='port1')
	port2 = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='port2')
	speed = models.CharField('Скорость связи', choices=Port.SPEED_CHOICES, max_length=20, blank=True, null=True)


class FavoriteColor(models.Model):
	title = models.CharField('Название', max_length=30)
	color = models.CharField('Цвет', max_length=30)
