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

def layer2view(parent, layer, pre_layer):
	info = {
			'name': layer['name'],
			'src': '@drawable/' + layer['name'],
			}

	# layout_marginTop
	if pre_layer:
		margin_top = layer['bounds'][1] - pre_layer['bounds'][3]
	else:
		margin_top = 0
	if margin_top != 0:
		info['layout_marginTop'] = str(margin_top) + 'dp'

	# layout_width, layout_gravity
	margin_left = layer['bounds'][0]
	margin_right = parent['width'] - layer['bounds'][2]
	if margin_left < 5 and margin_right < 5:
		info['layout_width'] = 'match_parent'
		info['scaleType'] = 'fitXY'
	else:
		info['layout_width'] = 'wrap_content'
		if abs(margin_left - margin_right) < 5:
			info['layout_gravity'] = 'center_horizontal'
	template = env.get_template('ImageView.xml')
	view = template.render(info=info)
	return view 

def sort_layers(layers):
	layers.sort(key = lambda l:l['bounds'][1])

def layerset2layout(layer_set, is_root=False):
	layers = layer_set['layers']
	sort_layers(layers)
	child_views = []
	for i in range(len(layers)):
		layer = layers[i]
		if i > 0:
			pre_layer = layers[i-1]
		else:
			pre_layer = None
		view = layer2view(layer_set, layer, pre_layer)
		child_views.append(view)
	child_views = ''.join(child_views)

	info = {'child_views': child_views}
	template = env.get_template('ScrollView.xml')
	layout = template.render(info=info)
	return layout

if __name__ == '__main__':
	s = open('out/layers.txt').read()
	doc = json.loads(s)

	# render xml
	env = init_env()

	root_layout = layerset2layout(doc, True)
	print root_layout

