// @include 'json.jsx'
// @include 'common.jsx'

function getLayersInfo(layers) {
	var _layers = [];
	for (var i=0; i<layers.length; i++) {
		var layer = layers[i];
		if (!filterLayer(layer))
			continue;

		var _layer = {};
		_layer.name = layer.name;
		_layer.left = layer.bounds[0].value;
		_layer.ttop = layer.bounds[1].value;
		_layer.right = layer.bounds[2].value;
		_layer.bottom = layer.bounds[3].value;

		if (layer.constructor == ArtLayer)
			_layer.kind = "" + layer.kind;
		else if (layer.constructor == LayerSet)
			_layer.layers = getLayersInfo(layer.layers);
		_layers.push(_layer);
	}
	return _layers;
}

function dumpDoc(doc) {
	var _doc = {}
	_doc.name = doc.name;
	_doc.width = doc.width.value;
	_doc.height = doc.height.value;
	_doc.layers = getLayersInfo(doc.layers);

	var file = File(proj_root + "out/layers.txt");
	file.open("e", "TEXT", "????");
	file.writeln(JSON.stringify(_doc));
	file.close();

	alert("OK");
}

function main() {
	init();
	var doc = app.activeDocument;
	var layers = doc.layers;
	dumpDoc(doc, layers);
}

main()

