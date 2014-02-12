#!/usr/bin/python

import sys
import re
import pprint
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader
import json
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

def layer2view(parent, layer):
	info = {
			'name': layer['name'],
			'src': '@drawable/' + layer['name'],
			}
	left_margin = layer['bounds'][0]
	right_margin = parent['width'] - layer['bounds'][2]
	if left_margin < 5 and right_margin < 5:
		info['layout_width'] = 'match_parent'
		info['scaleType'] = 'fitXY'
	else:
		info['layout_width'] = 'wrap_content'
		if abs(left_margin - right_margin) < 5:
			info['layout_gravity'] = 'center_horizontal'
	template = env.get_template('ImageView.xml')
	view = template.render(info=info)
	return view 

def layerset2layout(layer_set, is_root=False):
	child_views = []
	for layer in layer_set['layers']:
		view = layer2view(layer_set, layer)
		child_views.append(view)
	child_views = ''.join(child_views)

	layer_set['layout_type'] = 'LinearLayout'
	layer_set['orientation'] = 'vertical'
	layer_set['is_root'] = is_root
	layer_set['child_views'] = child_views
	template = env.get_template('LinearLayout.xml')
	layout = template.render(layer_set=layer_set)
	return layout

if __name__ == '__main__':
	s = open('out/layers.txt').read()
	doc = json.loads(s)

	# render xml
	env = init_env()

	root_layout = layerset2layout(doc, True)
	print root_layout

