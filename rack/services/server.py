from rack.models import Port
from rack.services.port import PortHelper


class ServerHelper:
	DEFAULT_COLOR = '#000000'

	def __init__(self, server=None):
		self.server = server

	@classmethod
	def create_server(cls, form):
		server = form.save()

		Port.objects.bulk_create(
			[
				Port(
					color=cls.DEFAULT_COLOR,
					speed=server.base_speed,
					material=server.base_material,
					server=server,
					number=number
				) for number in range(1, form.cleaned_data.get('count_ports') + 1)
			]
		)
		return server

	def delete_ports(self, id_ports):
		self.server.port_set.filter(pk__in=id_ports).delete()
		ports = PortHelper.ports_numbering(self.server.port_set.all().order_by('pk'))
		ports.bulk_update(ports, ['number'])


class ServerLengthParseError(Exception):
	pass


class ServerLengthParser:
	def __init__(self, string: str):
		self._string = string.strip().lower()

	def parse_string(self, unit: str):
		separators = ('1/3u', '1/3 u', 'u')
		res = None

		try:
			res = int(self._string)
			return res if unit == '1/3u' else res * 3

		except ValueError:
			for sep in separators:
				if self._string.endswith(sep):
					res = self._string.replace(sep, '').strip()

					try:
						res = int(res)
						return res if sep != 'u' else res * 3

					except ValueError:
						raise ServerLengthParseError('Не удалось расшифровать строку')
			raise ServerLengthParseError('Не удалось расшифровать строку')
