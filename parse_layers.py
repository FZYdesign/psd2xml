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

def layer2view(parent_bounds, layer, pre_layer=None):
	layer_width = layer['bounds'][2] - layer['bounds'][0]
	layer_height = layer['bounds'][3] - layer['bounds'][1]
	parent_width = parent_bounds[2] - parent_bounds[0]
	parent_height = parent_bounds[3] - parent_bounds[1]

	comment = ['layer_bounds: ' + str(layer['bounds']), 'parent_bounds: ' + str(parent_bounds)]

	info = {
			'name': layer['name'],
			'layout_width': 'wrap_content',
			}

	if parent_width -layer_width < parent_width / 10:
		info['layout_width'] = 'match_parent'
		info['background'] = '@drawable/' + layer['name']
	else:
		info['src'] = '@drawable/' + layer['name']
	template = env.get_template('ImageView.xml')
	view = template.render(info=info, comment=comment)
	return view 

def layer_group_to_layout(group):
	group_bounds = get_group_bounds(group)
	group.sort(key = lambda x:x['bounds'][0])

	info = {}
	child_views = []
	for i in range(len(group)):
		layer = group[i]
		# set background
		layer_width = layer['bounds'][2] - layer['bounds'][0]
		layer_height = layer['bounds'][3] - layer['bounds'][1]
		parent_width = group_bounds[2] - group_bounds[0]
		parent_height = group_bounds[3] - group_bounds[1]

		if layer_width > parent_width * 0.9 and layer_height > parent_height * 0.9:
			info['background'] = '@drawable/' + layer['name']
			continue

		# set pre_layer
		if i > 0:
			pre_layer = group[i-1]
		else:
			pre_layer = None

		view = layer2view(group_bounds, layer, pre_layer)
		child_views.append(view)
	child_views = ''.join(child_views)

	template = env.get_template('LinearLayout.xml')
	layout = template.render(info=info, child_views=child_views)
	return layout

def check_background(layer_bounds, group_bounds):
	layer_width = layer_bounds[2] - layer_bounds[0]
	layer_height = layer_bounds[3] - layer_bounds[1]
	group_width = group_bounds[2] - group_bounds[0]
	group_height = group_bounds[3] - group_bounds[1]

	if layer_width > group_width * 0.9 and layer_height > group_height * 0.9:
		return True

def group2layout(group, layout_type='LinearLayout'):
	childs = divide_group(group)
	child_views = []
	attr = {}
	for child in childs:
		if type(child) == list:
			child_view = group2layout(child)
			child_views.append(child_view)
		elif type(child) == dict:
			if check_background(child['bounds'], get_group_bounds(group)):
				attr['background'] = '@drawable/' + child['name']
			else:
				child_view = layer2view(get_group_bounds(group), child)
				child_views.append(child_view)
	child_views = ''.join(child_views)
	
	template = env.get_template(layout_type + '.xml')
	layout = template.render(childs=child_views, attr=attr)
	return layout

def get_group_bounds(group):
	bounds = [sys.maxint, sys.maxint, 0, 0]
	for layer in group:
		if layer['bounds'][0] < bounds[0]:
			bounds[0] = layer['bounds'][0]
		if layer['bounds'][1] < bounds[1]:
			bounds[1] = layer['bounds'][1]
		if layer['bounds'][2] > bounds[2]:
			bounds[2] = layer['bounds'][2]
		if layer['bounds'][3] > bounds[3]:
			bounds[3] = layer['bounds'][3]
	return bounds

def divide_group(layers_infos):
	_layers_infos = layers_infos[:]
	for layer_info in _layers_infos:
		layer_info['start'] = layer_info['bounds'][1]
		layer_info['end'] = layer_info['bounds'][3]
	_layers_infos.sort(key = lambda x:x['start'])

	groups = []
	group = [_layers_infos[0]]
	group_start = _layers_infos[0]['start']
	group_end = _layers_infos[0]['end']
	for i in range(1, len(_layers_infos)):
		if _layers_infos[i]['start'] < group_end - 5:
			group.append(_layers_infos[i])
			if _layers_infos[i]['end'] > group_end :
				group_end = _layers_infos[i]['end']
			else:
				group_end
		else:
			if len(group) > 1:
				groups.append(group)
			elif len(group) == 1:
				groups.append(group[0])
			group = [_layers_infos[i]]
			group_start = _layers_infos[i]['start']
			group_end = _layers_infos[i]['end']
	else:
		if len(group) > 1:
			groups.append(group)
		elif len(group) == 1:
			groups.append(group[0])
	
	if len(groups) == 1:
		groups = groups[0]

	return groups

def main():
	s = open('out/layers.txt').read().decode('gbk')
	doc = json.loads(s)
	doc['bounds'] = [0, 0, doc['width'], doc['height']]
	for layer in doc['layersInfo']:
		if layer['bounds'][0] < 0:
			layer['bounds'][1] = 0
		if layer['bounds'][1] < 0:
			layer['bounds'][1] = 0
		if layer['bounds'][2] > doc['width']:
			layer['bounds'][2] = doc['width']
		if layer['bounds'][3] > doc['height']:
			layer['bounds'][3] = doc['height']

	# render xml
	root_layout = group2layout(doc['layersInfo'], 'ScrollView')
	print root_layout
	exit()

	childs = divide_group(doc['layersInfo'])
	root_layout = layer_groups_to_layout(doc['bounds'], childs)
	print root_layout

if __name__ == '__main__':
	env = init_env()
	main()
