
// @include 'common.jsx'

function saveLayerImage(doc, layer, prefix) {
	try {
		_saveLayerImage(doc, layer, prefix);
	} catch (e) {
		alert('saveLayerImage: ' + layer + '\n' + e.description);
	}
}

function _saveLayerImage(doc, layer, prefix) {
	var layer_left = layer.bounds[0] > 0 ? layer.bounds[0] : 0;
	var layer_top = layer.bounds[1] > 0 ? layer.bounds[1] : 0;
	var layer_right = layer.bounds[2] < doc.width ? layer.bounds[2] : doc.width;
	var layer_bottom = layer.bounds[3] < doc.height ? layer.bounds[3] : doc.height;
	var layer_width = layer_right - layer_left;
	var layer_height = layer_bottom - layer_top;
	if (layer_width == 0 || layer_height == 0)
		return;

	layer.copy();

	filename = [prefix, layer.name].join('_').replace(new RegExp("[^_a-zA-Z0-9]", "g"), "_");
	var tmpDoc = app.documents.add(layer_width, layer_height, 72, filename, NewDocumentMode.RGB);
	app.activeDocument = tmpDoc;
	tmpDoc.paste();
	tmpDoc.layers[1].remove();
	tmpDoc.saveAs(new File(proj_root + "out/" + filename), new PNGSaveOptions());
	tmpDoc.close(SaveOptions.DONOTSAVECHANGES);
	app.activeDocument = doc;

}

function dumpImages(doc, layerSet, prefix, layerNum) {
	var layers = layerSet.layers;
	for (var i=0; i<layers.length; i++) {
		var layer = layers[i];
		if (!filterLayer(layer))
			continue;

		if (layer.constructor == LayerSet) {
			if (layerNum == 0) {
				dumpImages(doc, layer, [prefix, layer.name].join('_'), layerNum + 1);
			} else {
				layer = layer.merge();
				saveLayerImage(doc, layer, prefix);
			}
		} else
			saveLayerImage(doc, layer, prefix);
	}
}

function test(i) {
	var doc = app.activeDocument;
	var layers = doc.layers;
	saveLayerImage(doc, layers[i], 0);
}

function main() {
	init();
	var doc = app.activeDocument;
	dumpDoc(saveLayerImage, doc);
	//dumpImages(doc, doc, doc.name.replace('.psd', ''), 0);
	//test(0);
}

main();
