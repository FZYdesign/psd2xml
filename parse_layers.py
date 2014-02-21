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

	info = {
		'name': layer['name'],
		'layout_width': 'wrap_content',
	}

	if parent_width - layer_width < parent_width / 10:
		info['layout_width'] = 'match_parent'
		info['background'] = '@drawable/' + layer['name']
	else:
		info['src'] = '@drawable/' + layer['name']
	template = env.get_template('ImageView.xml')
	view = template.render(info=info)
	return view


def layer_group_to_layout(group):
	group_bounds = get_group_bounds(group)
	group.sort(key=lambda x: x['bounds'][0])

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
			pre_layer = group[i - 1]
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


def divide_group(group):
	_group = group[:]
	for layer in _group:
		layer['start'] = layer['bounds'][1]
		layer['end'] = layer['bounds'][3]
	_group.sort(key=lambda x: x['start'])

	# pick out background layer
	background_layer = None
	for layer in _group:
		if check_background(layer['bounds'], get_group_bounds(group)):
			background_layer = layer
			_group.remove(layer)

	# divide group into child groups
	childs = []
	child = [_group[0]]
	child_start = _group[0]['start']
	child_end = _group[0]['end']
	for layer in _group[1:]:
		# continue the child group
		if layer['start'] < child_end - 5:
			child.append(layer)
			if layer['end'] > child_end:
				child_end = layer['end']
		# complete one child group and start a new one
		else:
			if len(child) > 1:
				childs.append(child)
			elif len(child) == 1:
				childs.append(child[0])
			child = [layer]
			child_start = layer['start']
			child_end = layer['end']
	else:
		if len(child) > 1:
			childs.append(child)
		elif len(child) == 1:
			childs.append(child[0])

	if len(childs) == 1:
		childs = childs[0]

	return childs


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
