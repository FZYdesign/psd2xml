
var proj_root = "/Users/linyun/Documents/ws-test/psd2xml/";

function main() {
	app.preferences.typeUnits = TypeUnits.POINTS;
	app.preferences.rulerUnits = Units.POINTS;
	var doc = app.activeDocument;
	var layers = doc.layers;
	dumpLayers(doc, layers);
}

function getLayerName(doc, layer) {
	var layer_name = doc.name.replace(".psd", "") + "_" + layer.name.replace(new RegExp("[^_a-zA-Z0-9]", "g"), "_");
	return layer_name;
}

function getLayerInfo(doc, layer) {
	text = '==========\n';
	text += getLayerName(doc, layer) + '\n';
	text += layer.bounds + '\n';
	text += layer.kind;
	if (layer instanceof ArtLayer)
		text += 'ArtLayer\n';
	else if (layer instanceof LayerSet)
		text += 'LayerSet\n';
	text += '\n';
	return text;
}

function saveLayerImage(doc, layer) {
	var layer_left = layer.bounds[0] > 0 ? layer.bounds[0] : 0;
	var layer_top = layer.bounds[1] > 0 ? layer.bounds[1] : 0;
	var layer_right = layer.bounds[2] < doc.width ? layer.bounds[2] : doc.width;
	var layer_bottom = layer.bounds[3] < doc.height ? layer.bounds[3] : doc.height;
	var layer_width = layer_right - layer_left;
	var layer_height = layer_bottom - layer_top;

	layer.copy();
	var tmpDoc = app.documents.add(layer_width, layer_height, 72, getLayerName(doc, layer), NewDocumentMode.RGB);
	app.activeDocument = tmpDoc;
	tmpDoc.paste();
	tmpDoc.layers[1].remove();
	tmpDoc.saveAs(new File(proj_root + "out/" + getLayerName(doc, layer)), new PNGSaveOptions());
	tmpDoc.close(SaveOptions.DONOTSAVECHANGES);

}

function dumpLayers(doc, layers) {
	var text = doc.name + "\n"
		+ doc.width + "\n"
		+ doc.height + "\n";
	for (var i=0; i<layers.length; i++) {
		app.activeDocument = doc;
		var layer = layers[i];
		if (layer.kind == LayerKind.SOLIDFILL)
			continue;
		else if (layer.kind == undefined)
			layer = layer.merge();
		else if (layer.kind == LayerKind.SMARTOBJECT)
			continue;
		else if (layer.kind == LayerKind.BRIGHTNESSCONTRAST)
			continue;
		else if (layer.isBackgroundLayer)
			continue;

		text += getLayerInfo(doc, layer);
		saveLayerImage(doc, layer);
	}

	var file = File(proj_root + "out/layers.txt");
	file.open("e", "TEXT", "????");
	file.writeln(text);
	file.close();

	alert("OK");
}

main()

