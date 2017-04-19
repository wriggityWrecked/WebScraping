
def handleTextInput( text ):

	text = text.lower()

	if 'who knows' in text:
		return True, 'Jeff knows.'

	if 'llama' in text:
		return True, 'Tinaface!'

	if 'regulators' in text:
		return True, 'Mount up!'

	if 'destiny' in text:
		return True, 'Eyes up, guardian.'

	if 'what a save' in text:
		return True, 'SAVAGE'

	if 'name' in text:
		return True, 'droopy weiner, lol'

	if 'stout' in text:
		return True, 'dimah dozen'

	if 'rockin' in text:
		return True, 'Rockin, rockin and rollin\ndown to the beach I\'m strollin\n'
		+'but the seagulls poke at my head\nNOT FUN\n but the seagulls\nhmm\nstop it now\n'
		+'HOOOHAAAHOOHOOHOHOHA\nHOOHAHOHOHOHA\nHOOOHAHOHOHOHOHAHOHAHOHOHA\n\n'
		+'https://www.youtube.com/watch?v=DiCGkzwW_S8'

	if 'ok' in text:
		return True, 'WHAT A SAVE'

	if 'tired' in text:
		return True,'go to sleep, h03'

	if 'yeah' in text:
		return True, 'SOLAR ECLIPSES'

	if 'rickroll' in text:
		return True, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

	if 'thing' in text or 'stupid' in text:
		return True, 'WUBBA LUBBA DUB DUB'

	if 'what is your purpose' in text:
		return True, 'scrape the b33r, oh my god'

	if 'trade' in text:
		return True, ' sh1tl0rd confirmed'

	if 'cellar' in text:
		return True, 'as in MBC? sh1tl0rd confirmed'

	if 'jeff' in text:
		return True, 'get over yourself'

	if 'hey' in text or 'said' in text or 'on' in text:
		return True, 'I SAID HEY\nWHAT\'s GOING ON?!?!?!?!\n\n'
		+'https://www.youtube.com/watch?v=eh7lp9umG2I'

	if 'gandalf' or 'wizard' in text:
		return True, 'https://www.youtube.com/watch?v=Sagg08DrO5U'

	if 'nope' in text:
		return True, 'I\'m going to need you to take your opinions, and put \'em way up inside your butthole'

	return False, ""