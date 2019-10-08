import json
import re
import sublime, sublime_plugin

from .utils import is_lua, levenshtein

#
# Method Class
#
class Func:
	def __init__(self, name, data):
		self.name = name
		self.description = data.get('description', name)
		self.args = data.get('args', '')

	@property
	def completion(self):
		return '\t'.join((self.name, self.args)), self.description

	def match(self, name):
		return self.levenshtein(name)<.2

	def levenshtein(self, name):
		return levenshtein(self.name, name)

def get_tree_functions(tree):
	return (f if isinstance(f, Func) else Func(name, dict(args='package')) for name, f in tree.items())

#
# TFM helpers
#
class TFM:
	settings = {}
	tree = {}
	functions = []

	def __init__(self):
		try:
			TFM.settings = sublime.load_settings("SublimeFormice.sublime-setting")
			lang = TFM.settings.get("language", "en")

			raw = sublime.load_resource("Packages/SublimeFormice/{}-SublimeFormice.sublime-language".format(lang))
			TFM.functions = []
			TFM.tree = self.build_tree(json.loads(raw))
		except Exception as e:
			print(e)

	def build_tree(self, data):
		tree = {}
		for name, value in data.items():
			type = value.get("type", None)
			if type == "function":
				tree[name] = Func(name, value)
				TFM.functions.append(tree[name])
			elif type == "attribute":
				tree[name] = Func(name, value)
			elif type == "package":
				tree[name] = self.build_tree(value.get('content', {}))
			else:
				raise TypeError("The sublime-language file's format is invalid. Invalid type: {}.".format(type))

		return tree

	def get_autocomplete(self, word, path=None):
		if path is None:
			return [f.completion for f in self.functions if f.match(word)]

		tree = TFM.tree
		for name in path[:-1]:
			if isinstance(tree, Func) or name not in tree:
				return
			tree = tree[name]

		word = path[-1]
		completions = []

		if word == '':
			completions = [f.completion for f in get_tree_functions(tree)]
		elif isinstance(tree.get(word), dict):
			completions = [f.completion for f in get_tree_functions(tree)]
		elif isinstance(tree.get(word), Func):
			completions = [tree[word].completion]
		else:
			completions = [f.completion for f in get_tree_functions(tree) if f.match(word)]

		if len(completions):
			completions.sort()
			return completions, sublime.INHIBIT_EXPLICIT_COMPLETIONS


class SublimeFormiceEvent(TFM, sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		position = locations[0] if len(locations) else None

		if not is_lua(view, position):
			return

		line = view.substr(view.line(position))
		pos = view.rowcol(position)[1]

		amatch = re.match(r'^([\w.]+).*?$', line[pos:], re.M)
		bmatch = re.match(r'^.*?([\w.]+)$', line[:pos], re.M)

		result = ''
		if bmatch is not None:
			result += bmatch.group(1)
		if amatch is not None:
			result += amatch.group(1)

		path = [node for node in result.split('.')]

		if len(path) and path[-1]=='':
			path = [node for node in path if node] + ['']

		return self.get_autocomplete(prefix, path)
