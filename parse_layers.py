#!/usr/bin/python

import sys
import re
import pprint
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader
sys.path += ['..']

def init_env():
	# used to load the template in directory 'templates'
	package_loader = PackageLoader('psd2xml', 'templates')

	# used to load the template in the current directory running the script
	file_system_loader = FileSystemLoader('.')
	
	env = Environment(loader=ChoiceLoader([file_system_loader, package_loader]))
	return env

def bound2num(bound):
	return int(bound.replace('pt', '').strip());

if __name__ == '__main__':
	s = open('out/layers.txt').read()
	infos = s.split('=' * 10)

	# parse doc info
	doc = infos[0].strip()
	doc_name, doc_width, doc_height = doc.splitlines()
	doc_width = bound2num(doc_width)
	doc_height = bound2num(doc_height);

	# parse layers info
	layers = infos[1:]
	layers_info = []
	for layer in layers[1:]:
		layer = layer.strip()
		if not layer:
			continue

		name, bounds, layer_type = layer.splitlines()
		l, t, r, b = bounds = map(bound2num, bounds.split(','))
		info = { 'name': name.strip(),
				'bounds': bounds,
				'layer_type': layer_type,
				}
		if abs(l) < 5 and abs(r - doc_width) < 5:
			info['width'] = 'match_parent'
		else:
			info['widh'] = 'wrap_content'
		layers_info.append(info)
	layers_info = sorted(layers_info, key = lambda x:x['bounds'][1])

	# render xml
	env = init_env()
	content = ''
	for info in layers_info:
		template = env.get_template('linear_layout.xml')
		content += template.render(info=info)
	
	template = env.get_template('linear_root.xml')
	root_layout = template.render(content=content)

	print root_layout

