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


class Server(models.Model):
	title = models.CharField('Метка сервера', max_length=50)
	length = models.PositiveIntegerField('Размер')
	note = models.TextField('Заметки', blank=True, null=True)
	rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, null=True)
	color = models.CharField('Цвет', max_length=50)

	class Meta:
		verbose_name = 'Сервер'
		verbose_name_plural = 'Серверы'

	def __str__(self):
		return self.title
