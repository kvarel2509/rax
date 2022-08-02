from rack.forms import ServerNoteForm
from rack.models import Rack


class RackHelper:
	def __init__(self, rack: Rack):
		self.rack = rack

	def get_context_for_detail_view(self):
		rack = []
		empty_row = {'server': None, 'note_form': None, 'length': 1}
		servers = self.rack.server_set.all()

		for row in self.rack.space:
			if type(row) == int:
				rack.extend([empty_row] * row)
			else:
				server = servers.get(pk=row['id'])
				rack.append(
					{'server': server, 'note_form': ServerNoteForm(instance=server), 'length': server.length}
				)
				rack.extend([None] * (server.length - 1))

		return rack
