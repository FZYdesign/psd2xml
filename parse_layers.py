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


def layer2view(parent, layer, orientation, pre_layer=None):
	parent_bounds = parent['bounds']
	layer_width = layer['bounds'][2] - layer['bounds'][0]
	layer_height = layer['bounds'][3] - layer['bounds'][1]
	parent_width = parent_bounds[2] - parent_bounds[0]
	parent_height = parent_bounds[3] - parent_bounds[1]

	attr = {
	'name': layer['name'],
	'layout_width': 'wrap_content',
	}

	# layout_width and layout_height
	attr.update(get_layout_wh(layer['bounds'], parent))

	if layer_width > parent_width * 0.9:
		attr['background'] = '@drawable/' + layer['name']
	else:
		attr['src'] = '@drawable/' + layer['name']

	# get center
	gravity = getGravity(layer, parent)
	attr.update(gravity)

	template = env.get_template('ImageView.xml')
	view = template.render(attr=attr)

	return view


def check_background(layer_bounds, group_bounds):
	layer_width = layer_bounds[2] - layer_bounds[0]
	layer_height = layer_bounds[3] - layer_bounds[1]
	group_width = group_bounds[2] - group_bounds[0]
	group_height = group_bounds[3] - group_bounds[1]

	if layer_width > group_width * 0.9 and layer_height > group_height * 0.9:
		return True


def getGravity(layer, parent):
	if not parent:
		return {}

	bounds = layer['bounds']
	parent_bounds = parent['bounds']

	center_x = (bounds[0] + bounds[2]) / 2
	center_y = (bounds[1] + bounds[3]) / 2
	parent_center_x = (parent_bounds[0] + parent_bounds[2]) / 2
	parent_center_y = (parent_bounds[1] + parent_bounds[3]) / 2

	attr = {}
	layout_gravity = []
	if abs(center_x - parent_center_x) < (parent_bounds[2] - parent_bounds[0]) * 0.1:
		if parent['layout_type'] == 'RelativeLayout':
			attr['layout_centerHorizontal'] = 'true'
		else:
			layout_gravity.append('center_horizontal')
	if abs(center_y - parent_center_y) < (parent_bounds[3] - parent_bounds[1]) * 0.1:
		if parent['layout_type'] == 'RelativeLayout':
			attr['layout_centerVertical'] = 'true'
		else:
			layout_gravity.append('center_vertical')
	if parent_bounds[2] - bounds[2] < (parent_bounds[2] - parent_bounds[0]) * 0.1:
		if parent['layout_type'] == 'RelativeLayout':
			attr['layout_alignParentRight'] = 'true'
		else:
			layout_gravity.append('right')

	if layout_gravity:
		attr['layout_gravity'] = '|'.join(layout_gravity)
	return attr


def group2layout(group, parent=None):
	xmlns = ''
	if not parent:
		xmlns = 'xmlns:android="http://schemas.android.com/apk/res/android"'

	#
	# get attr
	#
	attr = {}

	# layout_width and layout_height
	attr.update(get_layout_wh(group['bounds'], parent))

	group['bounds'] = get_group_bounds(group['layers'])

	# pick out background layer
	background_layer = None
	for layer in group['layers']:
		if check_background(layer['bounds'], group['bounds']):
			background_layer = layer
			group['layers'].remove(layer)
	if background_layer:
		attr['background'] = '@drawable/' + background_layer['name']

	# divide group
	childs, orientation = divide_group(group['layers'])

	# get layout type
	if len(childs) == 1 and isinstance(childs[0], list):
		layout_type = 'RelativeLayout'
		childs = childs[0]
	elif len(childs) < 5:
		layout_type = 'RelativeLayout'
	else:
		if parent:
			layout_type = 'LinearLayout'
		else:
			layout_type = 'ScrollView'
	group['layout_type'] = layout_type

	# get gravity
	gravity = getGravity(group, parent)
	attr.update(gravity)

	# gen child views
	child_views = []
	for child in childs:
		if type(child) == list:
			child_group = {
			'layers': child,
			'bounds': get_group_bounds(child),
			}
			child_view = group2layout(child_group, group)
			child_views.append(child_view)
		elif type(child) == dict:
			child_view = layer2view(group, child, orientation)
			child_views.append(child_view)
	child_views = ''.join(child_views)
	attr['orientation'] = orientation

	template = env.get_template(layout_type + '.xml')
	layout = template.render(childs=child_views, attr=attr, xmlns=xmlns)
	return layout


def get_layout_wh(child_bounds, parent):
	attr = {
	'layout_width': 'wrap_content',
	'layout_height': 'wrap_content',
	}
	if not parent:
		return attr

	parent_bounds = parent['bounds']
	child_width = child_bounds[2] - child_bounds[0]
	child_height = child_bounds[3] - child_bounds[1]
	parent_width = parent_bounds[2] - parent_bounds[0]
	parent_height = parent_bounds[3] - parent_bounds[1]
	if child_width < parent_width * 0.9:
		attr['layout_width'] = 'wrap_content'
	if child_height < parent_height * 0.9:
		attr['layout_height'] = 'wrap_content'
	return attr


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
	_group.sort(cmp=cmp_layer)
	h_childs = _divide_group(_group)

	# vertical divide
	_group = group[:]
	for layer in _group:
		layer['start'] = layer['bounds'][1]
		layer['end'] = layer['bounds'][3]
	_group.sort(cmp=cmp_layer)
	v_childs = _divide_group(_group)

	if len(h_childs) > len(v_childs):
		childs = h_childs
		orientation = 'horizontal'
	else:
		childs = v_childs
		orientation = 'vertical'

	return childs, orientation


def cmp_layer(a, b):
	if a['start'] != b['start']:
		return a['start'] - b['start']
	else:
		return a['end'] - b['end']


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
	doc['layers'] = doc['layersInfo']

	# render xml
	root_layout = group2layout(doc)
	print root_layout
	exit()


if __name__ == '__main__':
	env = init_env()
	main()
