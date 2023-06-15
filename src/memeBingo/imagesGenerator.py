
from .models import CardModel, GameModel
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Literal



class ImagesGenerator:

	_cardSizeWithTitle = (626, 718)
	_cardSizeWithoutTitle = (626, 626)
	# _cardPadding = (8, 8)
	# _tileSize = (117, 117)
	# _tileMargin = (6, 6)
	# _tilePadding = (5, 5)
	_fontSizes = [(27, 18, 3), (45, 14, 3), (100500, 12, 4)]
	# _roundness = 8

	def __init__(self, assetsDir) -> None:
		self._assetsDir = assetsDir

	def wrap(self, draw: ImageDraw.ImageDraw, text: str, width: int, font:ImageFont):
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
	
	def getTileImage(self, tileColor, resize:float = 2, roundness = 8, tileSizeX = 117, tileSizeY = 117, tileMarginX = 6, tileMarginY = 6):

		resize = 3

		tileImage = Image.new('RGBA', (resize * (tileSizeX + tileMarginX * 2), 
				 						resize * (tileSizeY + tileMarginY * 2)), (0, 0, 0, 0))
		tileDraw = ImageDraw.Draw(tileImage)

		shadowColor = (0,0,0,50)

		x = resize * (tileMarginX)
		y = resize * (tileMarginY + 2)

		tileDraw.pieslice((x, y, 
							x + resize * (roundness*2), y + resize * (roundness*2)), 
							start=180, end=270, fill=shadowColor)
		tileDraw.pieslice((x, y + resize * (tileSizeX - roundness*2), 
							x + resize * (roundness*2), y + resize * (tileSizeY)), 
							start=90, end=180, fill=shadowColor)

		tileDraw.pieslice((x + resize * (tileSizeX - roundness*2), y, 
							x + resize * (tileSizeX), y + resize * (roundness*2)), 
							start=270, end=0, fill=shadowColor)
		tileDraw.pieslice((x + resize * (tileSizeX - roundness*2), y + resize * (tileSizeY - roundness*2), 
							x + resize * (tileSizeX), y + resize * (tileSizeY)), 
							start=0, end=90, fill=shadowColor)

		tileDraw.rectangle((x + resize * (roundness), y, 
							x + resize * (tileSizeX - roundness), y + resize * (tileSizeY)), 
							fill=shadowColor)
		tileDraw.rectangle((x, y + resize * (roundness), 
							x + resize * (tileSizeX), y + resize * (tileSizeY - roundness)), 
							fill=shadowColor)

		tileImage = tileImage.filter(ImageFilter.GaussianBlur(resize))
		tileDraw = ImageDraw.Draw(tileImage)

		y = resize * tileMarginY

		tileDraw.pieslice((x, y, 
							x + resize * (roundness*2), y + resize * (roundness*2)), 
							start=180, end=270, fill=tileColor)
		tileDraw.pieslice((x, y + resize * (tileSizeX - roundness*2), 
							x + resize * (roundness*2), y + resize * (tileSizeY)), 
							start=90, end=180, fill=tileColor)

		tileDraw.pieslice((x + resize * (tileSizeX - roundness*2), y, 
							x + resize * (tileSizeX), y + resize * (roundness*2)), 
							start=270, end=0, fill=tileColor)
		tileDraw.pieslice((x + resize * (tileSizeX - roundness*2), y + resize * (tileSizeY - roundness*2), 
							x + resize * (tileSizeX), y + resize * (tileSizeY)), 
							start=0, end=90, fill=tileColor)

		tileDraw.rectangle((x + resize * (roundness), y, 
							x + resize * (tileSizeX - roundness), y + resize * (tileSizeY)), 
							fill=tileColor)
		tileDraw.rectangle((x, y + resize * (roundness), 
							x + resize * (tileSizeX), y + resize * (tileSizeY - roundness)), 
							fill=tileColor)

		tileImage = tileImage.resize(((tileSizeX + tileMarginX * 2), 
				 						(tileSizeY + tileMarginY * 2)), Image.BILINEAR)
	
		return tileImage
	
	def parseColor(self, color:str):
		return tuple((int(color[1:3], 16), 
						int(color[3:5], 16), 
						int(color[5:7], 16)))
	
	def getFont(self):
		return self._assetsDir + "Roboto-Regular.ttf"

	def getCardImage(self, card:CardModel, size:Literal['full','small'] = 'full', withTitle:bool = False, 
		  tileSizeX = 117, tileSizeY = 117, tileMarginX = 6, tileMarginY = 6, paddingX = 8, paddingY = 8,
		  tilePaddingX = 5, tilePaddingY=5):

		phrases = dict(enumerate(card.phrases))

		tileColor = self.parseColor(card.appearance.get('tilesColor', '#ffffff')) + tuple([255])
		
		tileImage = self.getTileImage(tileColor=tileColor)

		bgColor = self.parseColor(card.appearance.get('backgroundColor', '#333333'))
		
		image = Image.new('RGBA', self._cardSizeWithTitle if withTitle else self._cardSizeWithoutTitle, bgColor)
		draw = ImageDraw.Draw(image)
		
		textColor = self.parseColor(card.appearance.get('textColor', '#666666'))

		for i in range(25):
			x = paddingX + (i % 5) * (tileSizeX + tileMarginX)
			y = paddingY + (i // 5) * (tileSizeY + tileMarginY)

			image.alpha_composite(tileImage, (x - tileMarginX, y - tileMarginY))

		for i in range(25):
			x = paddingX + (i % 5) * (tileSizeX + tileMarginX) + tilePaddingX
			y = paddingY + (i // 5) * (tileSizeY + tileMarginY) + tilePaddingY

			fontSize = [t for t in self._fontSizes if len(phrases.get(i, '')) < t[0]][0]
			font = ImageFont.truetype(font=self.getFont(), size=fontSize[1])
			innerX = tileSizeX - 2 * tilePaddingX
			innerY = tileSizeY - 2 * tilePaddingY
			wraped = "\n".join(self.wrap(draw = draw, text = phrases.get(i, ''), width = innerX, font=font)[0:fontSize[2]])
			bbox = draw.multiline_textbbox((0, 0), wraped, font=font, align='center')
			# print(bbox)
			draw.multiline_text((x + (innerX - bbox[2])//2, y + (innerY - bbox[3] + bbox[1])//2 ), wraped, font=font, align='center', fill=textColor)

		if size == 'small':
			image = image.resize((244,244), Image.BILINEAR)

		return image
	
	def getCheckImage(self, checkColor, tileSizeX = 117, tileSizeY = 117, tilePaddingX = 5, tilePaddingY=5):
		color = Image.new('RGBA', (tileSizeX - tilePaddingX*2, tileSizeY - tilePaddingY * 2), checkColor)

		mask = Image.open(self._assetsDir + "tileX1.png").convert('RGBA').resize(
			(tileSizeX - tilePaddingX*2, tileSizeY - tilePaddingY * 2), Image.BILINEAR).getchannel('A')
		
		mask = Image.eval(mask, (lambda x: x * 0.5))
		
		color.putalpha(mask)

		return color


	def getGameImage(self, card:CardModel, game: GameModel, size:Literal['full','small'] = 'full', withTitle:bool = False, 
		  tileSizeX = 117, tileSizeY = 117, tileMarginX = 6, tileMarginY = 6, paddingX = 8, paddingY = 8,
		  tilePaddingX = 5, tilePaddingY=5):
		
		image = self.getCardImage(card=card)

		checkColor = self.parseColor(card.appearance.get('markColor', '#ff3333'))

		checkImage = self.getCheckImage(checkColor=checkColor)

		for i in range(25):

			if i not in game.checkedPhrases:
				continue

			x = paddingX + (i % 5) * (tileSizeX + tileMarginX)
			y = paddingY + (i // 5) * (tileSizeY + tileMarginY)

			image.alpha_composite(checkImage, (x + tilePaddingX , y + tilePaddingY))


		if size == 'small':
			image = image.resize((244,244), Image.BILINEAR)

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

	gen = ImagesGenerator(assetsDir= PATH_FILES + 'src/assets/')
	card = CardModel(phrases=phrases.split('\n'), title='qweasd', description='', tags = [], authorId='123', 
					  appearance={}) # 'backgroundColor':'#5300eb', 'textColor':'#bed3f3', 'tilesColor':  '#db3e00'
	
	game = GameModel(checkedPhrases=[1,6,8,9,12,22], cardId='qweasd', ownerId='123')
	img = gen.getGameImage(card, game)
	img.show('asdasd')
	img.save('img.png')

