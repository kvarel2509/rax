def get_parsing_list(lst):
	result = []
	for value in lst:
		if isinstance(value, dict):
			result.append(value)
		elif value == 0:
			continue
		elif result and isinstance(result[-1], int):
			result[-1] += value
		else:
			result.append(value)
	return result


def get_new_space_after_move(server, space, move_type):
	index_start = space.index({'id': server.pk, 'length': server.length})
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
		for index, value in enumerate(space[index_start + 2:], start=index_start+2):
			if isinstance(value, int) and value >= server.length:
				space.insert(index + 1, value - server.length)
				space[index], space[index_start] = space[index_start], server.length
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
			if isinstance(space[index], int) and space[index] >= server.length:
				space[index] -= server.length
				space.insert(index + 1, space[index_start])
				space[index_start + 1] = server.length
				return space
	elif move_type == 'down_max':
		for index in range(len(space)-1, index_start, -1):
			if isinstance(space[index], int) and space[index] >= server.length:
				space.insert(index + 1, space[index_start])
				space[index_start], space[index] = server.length, space[index] - server.length
				return space
		if index_start + 1 < len(space) and isinstance(space[index_start+1], int):
			space[index_start], space[index_start+1] = space[index_start+1], space[index_start]
			return space
	elif move_type == 'up_max':
		for index in range(0, index_start):
			if isinstance(space[index], int) and space[index] >= server.length:
				space.insert(index, space[index_start])
				space[index+1] -= server.length
				space[index_start+1] = server.length
				return space
		if index_start > 0 and isinstance(space[index_start-1], int):
			space[index_start], space[index_start - 1] = space[index_start - 1], space[index_start]
			return space
	return False


def parser_length(length):
	length = length.lower()
	m = ['1/3u', 'u']
	for i in m:
		if i in length:
			x = length.split(i)
			try:
				return int(x[0].strip()) if i == '1/3u' else int(x[0].strip()) * 3
			except ValueError:
				return False
	return False


def get_space_after_delete(server):
	space = server.rack.space
	new_space = []
	for index, value in enumerate(space):
		if isinstance(value, dict) and value['id'] == server.pk:
			new_space.extend([value['length'], *space[index + 1:]])
			return new_space
		new_space.append(value)
