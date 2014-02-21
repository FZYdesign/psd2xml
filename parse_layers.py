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


def layer2view(parent_bounds, layer, orientation, pre_layer=None):
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

	if (orientation == 'horizontal' and layer['bounds'][2] + 5 > parent_bounds[2]) or \
			(orientation == 'vertical' and layer['bounds'][3] + 5 > parent_bounds[3]):
		template = env.get_template('Space.xml')
		view = template.render() + view

	return view


def check_background(layer_bounds, group_bounds):
	layer_width = layer_bounds[2] - layer_bounds[0]
	layer_height = layer_bounds[3] - layer_bounds[1]
	group_width = group_bounds[2] - group_bounds[0]
	group_height = group_bounds[3] - group_bounds[1]

	if layer_width > group_width * 0.9 and layer_height > group_height * 0.9:
		return True


def group2layout(group, layout_type='LinearLayout'):
	attr = {}
	group_bounds = get_group_bounds(group)

	# pick out background layer
	background_layer = None
	for layer in group:
		if check_background(layer['bounds'], group_bounds):
			background_layer = layer
			group.remove(layer)
	if background_layer:
		attr['background'] = '@drawable/' + background_layer['name']

	childs, orientation = divide_group(group)

	child_views = []
	for child in childs:
		if type(child) == list:
			child_view = group2layout(child)
			child_views.append(child_view)
		elif type(child) == dict:
			if check_background(child['bounds'], get_group_bounds(group)):
				attr['background'] = '@drawable/' + child['name']
			else:
				child_view = layer2view(get_group_bounds(group), child, orientation)
				child_views.append(child_view)
	child_views = ''.join(child_views)
	attr['orientation'] = orientation

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
	# horizontal divide
	_group = group[:]
	for layer in _group:
		layer['start'] = layer['bounds'][0]
		layer['end'] = layer['bounds'][2]
	_group.sort(key=lambda x: x['start'])
	h_childs = _divide_group(_group)

	# vertical divide
	_group = group[:]
	for layer in _group:
		layer['start'] = layer['bounds'][1]
		layer['end'] = layer['bounds'][3]
	_group.sort(key=lambda x: x['start'])
	v_childs = _divide_group(_group)

	if len(h_childs) > len(v_childs):
		childs = h_childs
		orientation = 'horizontal'
	else:
		childs = v_childs
		orientation = 'vertical'

	if len(childs) == 1:
		childs = childs[0]

	return childs, orientation

def _divide_group(_group):
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

if __name__ == '__main__':
	env = init_env()
	main()
