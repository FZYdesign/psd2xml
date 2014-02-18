#!/usr/bin/python

import sys
import re
import pprint
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader
import json
import md5
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

def layer_group_to_layout(group):
	group_bounds = [sys.maxint, sys.maxint, 0, 0]
	for layer in group:
		layer['start'] = layer['bounds'][0]
		layer['end'] = layer['bounds'][2]
		if layer['bounds'][0] < group_bounds[0]:
			group_bounds[0] = layer['bounds'][0]
		if layer['bounds'][1] < group_bounds[1]:
			group_bounds[1] = layer['bounds'][1]
		if layer['bounds'][2] > group_bounds[2]:
			group_bounds[2] = layer['bounds'][2]
		if layer['bounds'][3] > group_bounds[3]:
			group_bounds[3] = layer['bounds'][3]
	group.sort(key = lambda x:x['start'])
	child_views = []
	for i in range(len(group)):
		layer = group[i]
		if i > 0:
			pre_layer = group[i-1]
		else:
			pre_layer = None
		view = layer2view(group, layer, pre_layer)
		child_views.append(view)
	child_views = ''.join(child_views)

	info = {'child_views': child_views}
	template = env.get_template('LinearLayout.xml')
	layout = template.render(info=info)
	return layout


def layer_groups_to_layout(groups):
	child_layouts = []
	for group in groups:
		layout = layer_group_to_layout(group)
		child_layouts.append(layout)
	child_layouts = ''.join(child_layouts)
	
	info = {'childs': child_layouts}
	template = env.get_template('ScrollView.xml')
	layout = template.render(info=info)
	return layout

def get_layer_groups(layers_infos):
	_layers_infos = layers_infos[:]
	for layer_info in _layers_infos:
		layer_info['start'] = layer_info['bounds'][1]
		layer_info['end'] = layer_info['bounds'][3]
	_layers_infos.sort(key = lambda x:x['start'])
	groups = []
	group = [_layers_infos[0]]
	for i in range(1, len(_layers_infos)):
		if _layers_infos[i]['start'] < _layers_infos[i-1]['end']:
			group.append(_layers_infos[i])
		else:
			groups.append(group)
			group = [_layers_infos[i]]
	else:
		groups.append(group)

	return 'horizontal', groups

if __name__ == '__main__':
	s = open('out/layers.txt').read().decode('gbk')
	doc = json.loads(s)

	# render xml
	env = init_env()

	orientation, groups = get_layer_groups(doc['layersInfo'])
	
	root_layout = layer_groups_to_layout(groups)
	print root_layout

