from rack.models import Server, Port


class ServerHelper:
	DEFAULT_COLOR = '#000000'

	def __init__(self, server=None):
		self.server = server

	@classmethod
	def create_server(cls, cleaned_data):
		server = Server.objects.create(
			title=cleaned_data.get('title'),
			length=cleaned_data.get('length'),
			note=cleaned_data.get('note'),
			rack=cleaned_data.get('rack'),
			color=cleaned_data.get('color'),
			base_speed=cleaned_data.get('base_speed'),
			base_material=cleaned_data.get('base_material'),
		)
		default_port = Port(
			color=cls.DEFAULT_COLOR,
			speed=cleaned_data['base_speed'],
			material=cleaned_data['base_material'],
			server=server,
		)
		Port.objects.bulk_create([default_port] * cleaned_data['count_ports'])
		return server

	def delete_ports(self, ports):
		self.server.port_set.filter(pk__in=ports).delete()

	def as_row(self):
		return {'id': self.server.pk, 'length': self.server.length}


class ServerLengthParseError(Exception):
	pass


class ServerLengthParser:
	def __init__(self, string: str):
		self._string = string.strip()

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
