
var proj_root = "/Users/linyun/Documents/ws-test/psd2xml/";

function main() {
	var doc = app.activeDocument;
	var layers = doc.layers;
	dumpLayers(doc, layers);
}

function dumpLayers(doc, layers) {
	/*
	// save layer info
	var text = '';
	for (var i=0; i<layers.length; i++) {
		var layer = layers[i];
		text += '==========\n';
		text += layer.name + '\n';
		text += layer.bounds + '\n';
		text += layer.kind;
		if (layer instanceof ArtLayer)
			text += 'ArtLayer\n';
		else if (layer instanceof LayerSet)
			text += 'LayerSet\n';
		text += '\n';
	}
	var file = File(proj_root + "out/layers.txt");
	file.open("e", "TEXT", "????");
	file.writeln(text);
	file.close();
	*/

	// save layer image
	for (var i=0; i<layers.length; i++) {
		app.activeDocument = doc;
		var layer = layers[i];
		if (layer.kind == LayerKind.SOLIDFILL)
			continue;
		if (layer.kind == undefined)
			continue;
		if (layer.kind == LayerKind.SMARTOBJECT)
			continue;
		if (layer.kind == LayerKind.BRIGHTNESSCONTRAST)
			continue;

		var layer_left = layer.bounds[0] > 0 ? layer.bounds[0] : 0;
		var layer_top = layer.bounds[1] > 0 ? layer.bounds[1] : 0;
		var layer_right = layer.bounds[2] < doc.width ? layer.bounds[2] : doc.width;
		var layer_bottom = layer.bounds[3] < doc.height ? layer.bounds[3] : doc.height;
		var layer_width = layer_right - layer_left;
		var layer_height = layer_bottom - layer_top;
		var layer_filename = layer.name.replace(" ", "_").replace(":", "_");

		layer.copy();

		var tmpDoc = app.documents.add(layer_width, layer_height, 72, layer_filename, NewDocumentMode.RGB);
		app.activeDocument = tmpDoc;
		tmpDoc.paste();
		tmpDoc.layers[1].remove();
		tmpDoc.saveAs(new File(proj_root + "out/" + layer_filename));
		tmpDoc.close(SaveOptions.DONOTSAVECHANGES);
	}

	alert("OK");
}

main()

