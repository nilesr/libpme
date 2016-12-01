#!/usr/bin/env python3
# PNG Metadata Editor
# Niles Rogoff 2016
import zlib, copy
class color_types(object):
    GREYSCALE = 0
    RGB = 2
    PALETTE = 3
    GREYSCALE_WITH_ALPHA = 4
    RGB_WITH_ALPHA = 6
class PME(object):
	def _int(self, binary):
		return int.from_bytes(binary, byteorder="big")
	def _bytes(self, integer, length):
		return integer.to_bytes(length, "big")
	def __init__(self, filename=False):
		self._init = False
		self._magic_number = b'\x89PNG\r\n\x1a\n'
		self.filename = filename
		self.chunks = []
		if filename:
			f = open(self.filename, "rb")
			assert(f.read(8) == self._magic_number)
			while True:
				length = f.read(4)
				label = f.read(4)
				data = f.read(self._int(length))
				crc = f.read(4)
				self._verify_crc(label, data, crc)
				self.chunks.append([length, label, data, crc])
				if label == b"IEND":
					break
			assert(self.chunks[0][1] == b"IHDR")
			self.recalculate_properties()
		else:
			self.chunks = [
				[b"\0\0\0\0", b"IHDR", b"\0" * 13, b""],
				[b"\0\0\0\0", b"IDAT", b"", b""],
				[b"\0\0\0\0", b"IEND", b"", b""]
			]
			self.width = self.height = 0 # the user can decide
			self.bit_depth = 8 # a sane default
			self.color_type = color_types.RGB_WITH_ALPHA
			self.compression_method = 0
			self.filter_method = 0 # The only one as far as I know
			self.interlace_method = 0
			self._init = True
			self.recalculate_IHDR()
			for i in range(len(self.chunks)):
				self.recalculate_crc(i)
				self.recalculate_length(i)
	# The alternative to this is to have an useless property accessor for all seven properties. Trust me, this is better.
	def __setattr__(self, name, value):
		super(PME, self).__setattr__(name, value)
		if name in ["width", "height", "bit_depth", "color_type", "compression_method", "filter_method", "interlace_method"]:
			self.recalculate_IHDR()   
	def _calculate_crc(self, label, binary):
		calculated = zlib.crc32(label)
		calculated = zlib.crc32(binary, calculated) & 0xFFFFFFFF
		return calculated
	def _verify_crc(self, label, binary, crc):
		assert(self._calculate_crc(label, binary) == self._int(crc))
	def recalculate_properties(self):
		self.width =				self._int(self.chunks[0][2][0:4])
		self.height =				self._int(self.chunks[0][2][4:8])
		self.bit_depth =			self._int([self.chunks[0][2][8]])
		self.color_type =			self._int([self.chunks[0][2][9]])
		self.compression_method =   self._int([self.chunks[0][2][10]])
		self.filter_method =		self._int([self.chunks[0][2][11]])
		self.interlace_method =		self._int([self.chunks[0][2][12]])
	def recalculate_IHDR(self):
		if not self._init: return
		final = self._bytes(self.width, 4)
		final += self._bytes(self.height, 4)
		final += self._bytes(self.bit_depth, 1)
		final += self._bytes(self.color_type, 1)
		final += self._bytes(self.compression_method, 1)
		final += self._bytes(self.filter_method, 1)
		final += self._bytes(self.interlace_method, 1)
		self.chunks[0][2] = final
		self.recalculate_crc(0)
		self.recalculate_length(0)
	def _index(self, index):
		if type(index) == list:
			return self.chunks.index(index)
		if type(index) == str:
			index = bytes(index)
		if type(index) == bytes: # PLEASE FOR THE LOVE OF GOD DO NOT DO THIS
			index = [x[1] for x in self.chunks].index(index) # index
		return index
	def recalculate_crc(self, index):
		index = self._index(index)
		self.chunks[index][3] = self._bytes(self._calculate_crc(self.chunks[index][1], self.chunks[index][2]), 4)
	def recalculate_length(self, index):
		index = self._index(index)
		self.chunks[index][0] = self._bytes(len(self.chunks[index][2]), 4)
	def save(self,filename=False):
		if not filename:
			filename = self.filename
		f = open(filename, "wb")
		f.write(self._magic_number)
		for chunk in self.chunks:
			for field in chunk:
				f.write(field)
	decompress = zlib.decompress
	compress = zlib.compress

	def get_concatenated_idat_data(self):
		data = b""
		for chunk in self.chunks:
			if chunk[1] == b'IDAT':
				data += chunk[2]
		return data
	def write_raw_idat_data(self, data):
		i = 0
		for chunk in copy.deepcopy(self.chunks):
			if chunk[1] == b'IDAT':
				i += 1
				if i > 1:
					del self.chunks[self.chunks.index(chunk)]
		for index in range(len(self.chunks)):
			if self.chunks[index][1] == b'IDAT':
				self.chunks[index][2] = data
				self.recalculate_crc(index)
				self.recalculate_length(index)
				return True
		return False
