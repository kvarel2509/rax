from django.db import models
from django.urls import reverse


class Rack(models.Model):
	title = models.CharField('Название стойки', max_length=50)
	size = models.PositiveIntegerField('Размер', help_text='Размер измеряется в целых юнитах')
	space = models.JSONField('Пространство для серверов')

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
	connection = models.TextField('Объект на том конце', blank=True, null=True)

	class Meta:
		verbose_name = 'Порт'
		verbose_name_plural = 'Порты'

	def __str__(self):
		return f'{self.pk} - {self.speed}, {self.material}'


class Server(models.Model):
	title = models.CharField('Метка сервера', max_length=50)
	length = models.PositiveIntegerField('Размер')
	note = models.TextField('Заметки', blank=True, null=True)
	rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, null=True)
	color = models.CharField('Цвет', max_length=50)
	base_speed = models.CharField('Скорость порта', choices=Port.SPEED_CHOICES, max_length=20)
	base_material = models.CharField('Тип порта', choices=Port.MATERIAL_CHOICES, max_length=20)

	class Meta:
		verbose_name = 'Сервер'
		verbose_name_plural = 'Серверы'

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('server_detail', kwargs={'pk': self.pk})
