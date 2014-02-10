
var proj_root = "/Users/linyun/Documents/ws-test/psd2xml/";

function main() {
	var doc = app.activeDocument;
	var layers = doc.layers;
	dumpLayers(doc, layers);
}

function dumpLayers(doc, layers) {
	var text = '';
	for (var i=0; i<layers.length; i++) {
		// save layer info
		var layer = layers[i];
		var layer_filename = layer.name.replace(" ", "_").replace(":", "_").replace("\/", "_");
		text += '==========\n';
		text += layer_filename + '\n';
		text += layer.bounds + '\n';
		text += layer.kind;
		if (layer instanceof ArtLayer)
			text += 'ArtLayer\n';
		else if (layer instanceof LayerSet)
			text += 'LayerSet\n';
		text += '\n';

		// save layer image
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

		var layer_left = layer.bounds[0] > 0 ? layer.bounds[0] : 0;
		var layer_top = layer.bounds[1] > 0 ? layer.bounds[1] : 0;
		var layer_right = layer.bounds[2] < doc.width ? layer.bounds[2] : doc.width;
		var layer_bottom = layer.bounds[3] < doc.height ? layer.bounds[3] : doc.height;
		var layer_width = layer_right - layer_left;
		var layer_height = layer_bottom - layer_top;

		layer.copy();

		var tmpDoc = app.documents.add(layer_width, layer_height, 72, layer_filename, NewDocumentMode.RGB);
		app.activeDocument = tmpDoc;
		tmpDoc.paste();
		tmpDoc.layers[1].remove();
		tmpDoc.saveAs(new File(proj_root + "out/" + layer_filename), new PNGSaveOptions());
		tmpDoc.close(SaveOptions.DONOTSAVECHANGES);
	}

	var file = File(proj_root + "out/layers.txt");
	file.open("e", "TEXT", "????");
	file.writeln(text);
	file.close();

	alert("OK");
}

main()

