from rack.forms import ServerNoteForm
from rack.models import Rack
from rack.services.server import ServerHelper


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

	def check_free_space(self, server_length):
		return any(map(lambda x: type(x) == int and x >= server_length, self.rack.space))

	def put_server_in_space(self, server: ServerHelper):
		new_space = []
		for ind, row in enumerate(self.rack.space):
			if type(row) != int or row < server.server.length:
				new_space.append(row)
			else:
				new_space.extend(
					[server.as_row(), row - server.server.length, *self.rack.space[ind + 1:]]
				)
				self.rack.space = self._normalize_space(new_space)
				server.server.rack.save()
				return server.server.rack

		raise AttributeError('Сервер не добавлен: недостаточно места')

	def delete_server_from_space(self, server):
		new_space = list(self.rack.space).copy()
		target = server.as_row()
		ind = new_space.index(target)
		new_space[ind] = target['length']
		self.rack.space = self._normalize_space(new_space)
		self.rack.save()
		return self.rack

	def move_server_in_space(self, server: ServerHelper, move_type: str):
		target = server.as_row()
		space = list(self.rack.space).copy()
		new_space = self._move_server(target, space, move_type)
		self.rack.space = self._normalize_space(new_space)
		self.rack.save()
		return self.rack

	@staticmethod
	def _move_server(target, space, move_type):
		index_start = space.index(target)

		if move_type in ['down1', 'down3'] and index_start + 1 < len(space):
			if move_type == 'down1':
				if isinstance(space[index_start + 1], int):
					space[index_start + 1] -= 1
					space.insert(index_start, 1)
					return space
			else:
				if isinstance(space[index_start + 1], int) and space[index_start + 1] >= 3:
					space[index_start + 1] -= 3
					space.insert(index_start, 3)
					return space
			for index, value in enumerate(space[index_start + 2:], start=index_start + 2):
				if isinstance(value, int) and value >= target['length']:
					space.insert(index + 1, value - target['length'])
					space[index], space[index_start] = space[index_start], target['length']
					return space
		elif move_type in ['up1', 'up3'] and index_start > 0:
			if move_type == 'up1':
				if isinstance(space[index_start - 1], int):
					space[index_start - 1] -= 1
					space.insert(index_start + 1, 1)
					return space
			else:
				if isinstance(space[index_start - 1], int) and space[index_start - 1] >= 3:
					space[index_start - 1] -= 3
					space.insert(index_start + 1, 3)
					return space
			for index in range(index_start - 2, -1, -1):
				if isinstance(space[index], int) and space[index] >= target['length']:
					space[index] -= target['length']
					space.insert(index + 1, space[index_start])
					space[index_start + 1] = target['length']
					return space
		elif move_type == 'down_max':
			for index in range(len(space) - 1, index_start, -1):
				if isinstance(space[index], int) and space[index] >= target['length']:
					space.insert(index + 1, space[index_start])
					space[index_start], space[index] = target['length'], space[index] - target['length']
					return space
			if index_start + 1 < len(space) and isinstance(space[index_start + 1], int):
				space[index_start], space[index_start + 1] = space[index_start + 1], space[index_start]
				return space
		elif move_type == 'up_max':
			for index in range(0, index_start):
				if isinstance(space[index], int) and space[index] >= target['length']:
					space.insert(index, space[index_start])
					space[index + 1] -= target['length']
					space[index_start + 1] = target['length']
					return space
			if index_start > 0 and isinstance(space[index_start - 1], int):
				space[index_start], space[index_start - 1] = space[index_start - 1], space[index_start]
				return space
		return space

	@staticmethod
	def _normalize_space(space):
		new_space = []

		for value in space:
			if type(value) == int and new_space and type(new_space[-1]) == int:
				new_space[-1] += value
			else:
				new_space.append(value)

		return new_space
