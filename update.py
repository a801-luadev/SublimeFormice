import json
import re
import requests

from bs4 import BeautifulSoup as BS

with requests.get('https://atelier801.com/topic?f=5&t=451587&p=1') as r:
	bs = BS(r.content, 'html.parser')
	raw_events = bs.find('div', id='tab_1_message_3').text
	raw_functions = bs.find('div', id='tab_2_message_3').text

tree = {}

for match in re.finditer(r'•\s*([^\s]+)\s+\(\s*(.*?)\s*\)\s*(.+?)\s*(Parameters:|•)', raw_functions):
	name, args, description, _ = match.groups()
	*path, name = name.split('.')

	current = tree
	for node in path:
		if node not in current:
			current[node] = {'type':'package', 'name':node, 'content':{}}
		current = current[node]['content']

	current[name] = {
		'args': args,
		'description': re.search(r'^(.+?)(| Note: .+)$', description).group(1),
		'type': 'function'
	}

with open('en-SublimeFormice.sublime-language', 'w', encoding='utf-8') as f:
	json.dump(tree, f, indent='\t')