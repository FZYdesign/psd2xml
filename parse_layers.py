#!/usr/bin/python

import re
import pprint

s = open('layers.txt').read()

layers = s.split('=' * 10)
layers_info = []
for layer in layers:
	layer = layer.strip()
	name, bounds, layer_type = layer.splitlines()
	layers_info.append({
		'name': name,
		'bounds': bounds,
		'layer_type': layer_type,
		})


