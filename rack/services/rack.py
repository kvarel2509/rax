from rack.models import Rack, Server


class NoFreePositionOnRackError(Exception):
	pass


class RackHelper:
	def __init__(self, rack: Rack):
		self.rack = rack

	def create_rack_backside(self):
		rack_backside = Rack.objects.create(
			title=self.rack.title,
			size=self.rack.size,
			backside=True,
		)
		rack_backside.reverse_side.add(self.rack)
		return rack_backside

	def get_free_position(self, server_applicant: Server, iterator_position: iter) -> int:
		print(iterator_position)
		servers = self.rack.server_set.exclude(pk=server_applicant.pk)

		for position in iterator_position:
			if all([not any([
				server.position <= position < server.position + server.length,
				server.position < position + server_applicant.length <= server.position + server.length,
				position <= server.position < position + server_applicant.length,
				position < server.position + server.length <= position + server_applicant.length
			]) for server in servers]):
				return position
		raise NoFreePositionOnRackError('Не удалось найти свободную позицию для сервера')
