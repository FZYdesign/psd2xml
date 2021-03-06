
// @include 'common.jsx'

function saveLayerImage(doc, layer, prefix) {
	try {
		_saveLayerImage(doc, layer, prefix);
	} catch (e) {
		alert('saveLayerImage: ' + layer + '\n' + e.description);
	}
}

function _saveLayerImage(doc, layer, prefix) {
	layer.copy();

	filename = [prefix, layer.name].join('_');
	filename = filterName(filename)
	var tmpDoc = app.documents.add(layer.width, layer.height, 72, filename, NewDocumentMode.RGB);
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

function toSmartObj(doc, layer, prefix) {
	doc.activeLayer = layer;
	executeAction(app.stringIDToTypeID('newPlacedLayer'), undefined, DialogModes.NO);
}

function main() {
	init();
	var doc = app.activeDocument;
	//dumpDoc(toSmartObj, doc);
	dumpDoc(saveLayerImage, doc);
}

main();
