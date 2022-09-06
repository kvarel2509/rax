from re import search
from typing import NamedTuple
from rack.models import Server, Port


class ProcessedSketchTuple(NamedTuple):
	server: int
	port: int
	speed: str


class PortConnectorParserTuple(NamedTuple):
	script: ProcessedSketchTuple
	string: str


class PortNotFoundError(Exception):
	pass


class PortIsNotFreeError(Exception):
	pass


class PortHelper:
	@staticmethod
	def search_port(script: ProcessedSketchTuple):
		server = Server.objects.filter(pk=script.server).first()

		if not server:
			raise PortNotFoundError(f'Сервер c pk={script.server} не существует')

		port = server.port_set.filter(number=script.port).first()

		if not port:
			raise PortNotFoundError(f'Порт с порядковым номером {script.port} не существует')

		return port

	@staticmethod
	def check_port_free(port: Port):
		if port.link.exists():
			raise PortIsNotFreeError('Запрошенный порт занят, необходимо удалить существующую связь')

	@staticmethod
	def ports_numbering(ports, start=1):
		for ind, port in enumerate(ports, start):
			port.number = ind
		return ports


class PortConnectionParser:
	PATTERN = r'^((?:#\d+){2,3})? *(.*)'
	SPEED_MATCHING = {10: '10Mbit', 100: '100Mbit', 1000: '1Gbit', 10000: '10Gbit'}

	def __init__(self, string: str):
		self._string = string

	def parse(self):
		match = search(self.PATTERN, self._string)

		if match.group(1):
			sketch = [int(i) for i in match.group(1).split('#')[1:]]
			speed = self.SPEED_MATCHING.get(sketch[2]) if len(sketch) == 3 else None
			script = ProcessedSketchTuple(server=sketch[0], port=sketch[1], speed=speed)
		else:
			script = None

		return PortConnectorParserTuple(script=script, string=match.group(2))
