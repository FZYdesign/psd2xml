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


if __name__ == '__main__':
	s = open('out/layers.txt').read()

	layers = s.split('=' * 10)
	layers_info = []
	for layer in layers:
		layer = layer.strip()
		if not layer:
			continue
		name, bounds, layer_type = layer.splitlines()
		bounds = map(float, bounds.replace(' cm', '').split(','))
		layers_info.append({
			'name': name.strip(),
			'bounds': bounds,
			'layer_type': layer_type,
			})

	layers_info = sorted(layers_info, key = lambda x:x['bounds'][1])
	pprint.pprint(layers_info)

	# render xml
	env = init_env()
	content = ''
	for info in layers_info:
		template = env.get_template('linear_layout.xml')
		content += template.render(info=info)
	
	template = env.get_template('linear_root.xml')
	root_layout = template.render(content=content)

	print root_layout

