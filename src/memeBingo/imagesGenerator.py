
from .models import CardModel
import re
from PIL import Image, ImageDraw, ImageFont

def wrap(draw: ImageDraw.ImageDraw, text: str, width: int, font:ImageFont):
	''' Каждый раз наращиваем строку пословно, 
		если первое слово слишком длинное - то побуквенно, 
		если выходим из длины, используем предыдущий вариант'''
	lines = []
	while len(text):
		words = re.split("(\s)", text)
		# print(words)
		word = words.pop(0)
		firstWordWidth = draw.multiline_textbbox((0,0), text=word, font=font)[2]
		# print(firstWordWidth, width)
		if firstWordWidth > width:
			current = last = ''
			lineWidth = 0
			while lineWidth <= width and len(word):
				letter = word[0]
				current = current + letter
				word = word[1:]
				lineWidth = draw.multiline_textbbox((0,0), text=current, font=font)[2]
				if lineWidth <= width:
					last = current
			
		else:
			lineWidth = firstWordWidth
			current = last = word
			while lineWidth <= width and len(words):
				word = words.pop(0)
				current = current + word
				lineWidth = draw.multiline_textbbox((0,0), text=current, font=font)[2]
				# print(lineWidth)
				if lineWidth <= width:
					last = current
				else: 
					words.insert(0, word)
			
		lines.append(last.strip())
		text = text[len(last):]
		
	# print(lines, text, lineWidth)
	return lines

class ImagesGenerator:

	_cardSizeWithTitle = (626, 718)
	_cardSizeWithoutTitle = (626, 626)
	_cardPadding = (8, 8)
	_tileSize = (117, 117)
	_tileMargin = (6, 6)
	_tilePadding = (5, 5)
	_fontSizes = [(27, 18, 3), (45, 14, 3), (100500, 12, 4)]
	_roundness = 8

	def __init__(self, font) -> None:
		self._font = font

	def getCardPNG(self, card:CardModel, size:str = 'full', withTitle:bool = False):

		phrases = dict(enumerate(card.phrases))

		bgColor = (int(card.appearance['backgroundColor'][1:3], 16), 
					int(card.appearance['backgroundColor'][3:5], 16), 
					int(card.appearance['backgroundColor'][5:7], 16))
		
		image = Image.new('RGB', self._cardSizeWithTitle if withTitle else self._cardSizeWithoutTitle, bgColor)
		draw = ImageDraw.Draw(image)

		tileColor = (int(card.appearance['tilesColor'][1:3], 16), 
						int(card.appearance['tilesColor'][3:5], 16), 
						int(card.appearance['tilesColor'][5:7], 16))
		
		textColor = (int(card.appearance['textColor'][1:3], 16), 
						int(card.appearance['textColor'][3:5], 16), 
						int(card.appearance['textColor'][5:7], 16))


		for i in range(25):
			x = self._cardPadding[0] + (i % 5) * (self._tileSize[0] + self._tileMargin[0])
			y = self._cardPadding[1] + (i // 5) * (self._tileSize[1] + self._tileMargin[1])

			draw.pieslice((x, y, x + self._roundness*2, y + self._roundness*2), start=180, end=270, fill=tileColor)
			draw.pieslice((x, y + self._tileSize[0] - self._roundness*2, x + self._roundness*2, y + self._tileSize[0]), start=90, end=180, fill=tileColor)

			draw.pieslice((x + self._tileSize[0] - self._roundness*2, y, x + self._tileSize[0], y + self._roundness*2), start=270, end=0, fill=tileColor)
			draw.pieslice((x + self._tileSize[0] - self._roundness*2, y + self._tileSize[0] - self._roundness*2, x + self._tileSize[0], y + self._tileSize[0]), start=0, end=90, fill=tileColor)

			draw.rectangle((x + self._roundness, y, x + self._tileSize[0] - self._roundness, y + self._tileSize[0]), fill=tileColor)
			draw.rectangle((x, y + self._roundness, x + self._tileSize[0], y + self._tileSize[0] - self._roundness), fill=tileColor)


		for i in range(25):
			x = self._cardPadding[0] + (i % 5) * (self._tileSize[0] + self._tileMargin[0]) + self._tilePadding[0]
			y = self._cardPadding[1] + (i // 5) * (self._tileSize[1] + self._tileMargin[1]) + self._tilePadding[1]
			fontSize = [t for t in self._fontSizes if len(phrases.get(i, '')) < t[0]][0]
			font = ImageFont.truetype(font=self._font, size=fontSize[1])
			inner = self._tileSize[0] - 2 * self._tilePadding[0]
			wraped = "\n".join(wrap(draw = draw, text = phrases.get(i, ''), width = inner, font=font))
			bbox = draw.multiline_textbbox((0, 0), wraped, font=font, align='center')
			# print(bbox)
			draw.multiline_text((x + (inner - bbox[2])//2, y + (inner - bbox[3])//2), wraped, font=font, align='center', fill=textColor)

		return image


if __name__ == '__main__':
	phrases = '''The bewildered tourist was lost.
The lost puppy was a wet and stinky dog.
The flu clinic had seen many cases of infectious disease.
It was a story as old as time.
The sports car drove the long and winding road.
Хрен моржовый (utf8 test)
Длииииииннннннннаое слооооовоооооо
Saturday became a cool, wet afternoon.
He was waiting for the rain to stop.
She was upset when it didn't boil.
You have been sleeping for a long time.
You might enjoy a massage.
He was eager to eat dinner.
Taking my dog for a walk is fun.
Walking in the rain can be difficult.
Strolling along a beach at sunset is romantic.
Getting a promotion is exciting.
Signing autographs takes time.
Going for ice cream is a real treat.
Singing for his supper was how he earned his keep.
Getting a sore back was the result of the golf game.
Pulling an all-nighter did not improve his test scores.
Sailing into the sunset was the perfect end to the book.
To make lemonade, you have to start with lemons.
I tried to see the stage, but I was too short.
She organized a boycott to make a statement.
To see Niagara Falls is mind-boggling.
He really needs to get his priorities in order.
The company decided to reduce hours for everyone.
To donate time or money is an honorable thing.
I went to Spain to study the language and culture.
'''
	from os import getcwd
	PATH_FILES = getcwd() + "/"
	print(PATH_FILES)

	gen = ImagesGenerator(font = PATH_FILES + "assets/Roboto-Regular.ttf" )
	model = CardModel(phrases=phrases.split('\n'), title='qweasd', description='', tags = [], authorId='123', 
					  appearance={'backgroundColor':'#5300eb', 'textColor':'#bed3f3', 'tilesColor':  '#db3e00'})
	img = gen.getCardPNG(model)
	img.show('asdasd')
	img.save('img.png')

