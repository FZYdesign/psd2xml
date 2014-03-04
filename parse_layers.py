#!/usr/bin/python

import sys
import re
import pprint
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader
import json
import md5
import math

sys.path += ['..']


def init_env():
    # used to load the template in directory 'templates'
    package_loader = PackageLoader('psd2xml', 'templates')

    # used to load the template in the current directory running the script
    file_system_loader = FileSystemLoader('.')

    env = Environment(loader=ChoiceLoader([file_system_loader, package_loader]))
    return env


def layer2view(parent, layer, pre_layer=None):
    parent_bounds = parent['bounds']
    layer_width = layer['bounds'][2] - layer['bounds'][0]
    layer_height = layer['bounds'][3] - layer['bounds'][1]
    parent_width = parent_bounds[2] - parent_bounds[0]
    parent_height = parent_bounds[3] - parent_bounds[1]

    attr = {
    'id': '@+id/' + layer['name'],
    'layout_width': 'wrap_content',
    }

    if layer.get('attr'):
        attr.update(layer['attr'])

    # layout_width and layout_height
    attr.update(get_layout_wh(layer['bounds'], parent))

    if layer_width > parent_width * 0.9:
        attr['background'] = '@drawable/' + layer['name']
    else:
        attr['src'] = '@drawable/' + layer['name']

    # get center
    gravity = get_gravity(layer, parent)
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


def get_gravity(layer, parent, parent_layout_type=None):
    if not parent:
        return {}
    h_gravity, v_gravity = _get_gravity(layer, parent)
    if not parent_layout_type:
        parent_layout_type = parent['layout_type']
    return trans_gravity(h_gravity, v_gravity, parent_layout_type)


def trans_gravity(h_gravity, v_gravity, parent_layout_type):
    attr = {}
    layout_gravity = []
    if (parent_layout_type == 'RelativeLayout'):
        if h_gravity == 'center':
            attr['layout_centerHorizontal'] = 'true'
        elif h_gravity == 'left':
            attr['layout_alignParentLeft'] = 'true'
        elif h_gravity == 'right':
            attr['layout_alignParentRight'] = 'true'

        if v_gravity == 'center':
            attr['layout_centerVertical'] = 'true'
        elif v_gravity == 'left':
            attr['layout_alignParentTop'] = 'true'
        elif v_gravity == 'right':
            attr['layout_alignParentBottom'] = 'true'
        return attr
    else:
        if h_gravity == 'center':
            layout_gravity.append('center_horizontal')
        elif h_gravity == 'left':
            layout_gravity.append('left')
        elif h_gravity == 'right':
            layout_gravity.append('right')

        if v_gravity == 'center':
            layout_gravity.append('center_horizontal')
        elif v_gravity == 'left':
            layout_gravity.append('top')
        elif v_gravity == 'right':
            layout_gravity.append('bottom')
        return {'layout_gravity': '|'.join(layout_gravity)}


def _get_gravity(layer, parent):
    parent_left = parent['bounds'][0]
    parent_top = parent['bounds'][1]
    parent_right = parent['bounds'][2]
    parent_bottom = parent['bounds'][3]
    parent_center_h, parent_center_v = get_center(parent['bounds'])
    layer_left = layer['bounds'][0]
    layer_top = layer['bounds'][1]
    layer_right = layer['bounds'][2]
    layer_bottom = layer['bounds'][3]

    layer_radius = (layer_right - layer_left + layer_bottom - layer_top) / 2
    v_gravity = None
    h_gravity = None

    if parent_center_h > layer_left and parent_center_h < layer_right:
        h_gravity = 'center'
    elif abs(layer_left - parent_left) < layer_radius:
        h_gravity = 'left'
    elif abs(layer_right - parent_right) < layer_radius:
        h_gravity = 'right'

    if parent_center_v > layer_top and parent_center_v < layer_bottom:
        v_gravity = 'center'
    elif abs(layer_top - parent_top) < layer_radius:
        v_gravity = 'top'
    elif abs(layer_bottom - parent_bottom) < layer_radius:
        v_gravity = 'bottom'

    return h_gravity, v_gravity


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
    bg_layers = []
    for layer in group['layers']:
        if check_background(layer['bounds'], group['bounds']):
            bg_layers.append(layer)
    for layer in bg_layers:
        group['layers'].remove(layer)
    if bg_layers:
        attr['background'] = '@drawable/' + bg_layers[len(bg_layers) - 1]['name']

    # get gravity
    gravity = get_gravity(group, parent)
    attr.update(gravity)

    if not group['layers']:
        group['layout_type'] = 'RelativeLayout'
        template = env.get_template(group['layout_type'] + '.xml')
        layout = template.render(attr=attr, xmlns=xmlns)
        return layout

    # divide group
    childs, layout_type, orientation = divide_group(group)
    if len(childs) == 1 and not bg_layers:
        childs = childs[0]
    if layout_type == 'LinearLayout' and not parent:
        layout_type = 'ScrollView'
    if orientation:
        attr['orientation'] = orientation
    group['layout_type'] = layout_type

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
            child_view = layer2view(group, child)
            child_views.append(child_view)
    child_views = ''.join(child_views)

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
    if child_width > parent_width * 0.9:
        attr['layout_width'] = 'wrap_content'
    if child_height > parent_height * 0.9:
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


def get_center(bounds):
    return (bounds[2] + bounds[0]) / 2, (bounds[3] + bounds[1]) / 2


def get_distance(p1, p2):
    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))


def get_key_points(bounds):
    left = bounds[0]
    top = bounds[1]
    right = bounds[2]
    bottom = bounds[3]
    center = get_center(bounds)
    center_h, center_v = center

    points = ((left, top), (center_h, top), (right, top),
              (left, center_v), (center_h, center_v), (right, center_v),
              (left, bottom), (center_h, bottom), (right, bottom),
    )
    return points


def is_relative_layout(group, childs):
    for child in childs:
        h_gravity, v_gravity = _get_gravity(child, group)
        if not h_gravity or not v_gravity:
            return False
        attr = get_gravity(child, group, 'RelativeLayout')
        if child.get('attr'):
            attr.update(child['attr'])
        child['attr'] = attr
    return True


def divide_group(group):
    # vertical divide
    layers = group['layers'][:]
    for layer in layers:
        layer['start'] = layer['bounds'][1]
        layer['end'] = layer['bounds'][3]
    layers.sort(cmp=cmp_layer)
    v_childs = _divide_group(layers)
    if (len(v_childs) > 3):
        return v_childs, 'LinearLayout', 'vertical'

    # horizontal divide
    layers = group['layers'][:]
    for layer in layers:
        layer['start'] = layer['bounds'][0]
        layer['end'] = layer['bounds'][2]
    layers.sort(cmp=cmp_layer)
    h_childs = _divide_group(layers)
    if (len(h_childs) > 3):
        return h_childs, 'LinearLayout', 'horizontal'

    if len(v_childs) > len(h_childs):
        childs = v_childs
        orientation = 'vertical'
    else:
        childs = h_childs
        orientation = 'horizontal'

    if len(childs) == 1 and isinstance(childs[0], list):
        return childs, 'RelativeLayout', None

    if is_relative_layout(group, group['layers']):
        return group['layers'], 'RelativeLayout', None

    return childs, 'LinearLayout', orientation


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
