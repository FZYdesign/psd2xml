
// @include 'common.jsx'

function saveLayerImage(doc, layer) {
	if (!filterLayer(layer))
		return;

	var layer_left = layer.bounds[0] > 0 ? layer.bounds[0] : 0;
	var layer_top = layer.bounds[1] > 0 ? layer.bounds[1] : 0;
	var layer_right = layer.bounds[2] < doc.width ? layer.bounds[2] : doc.width;
	var layer_bottom = layer.bounds[3] < doc.height ? layer.bounds[3] : doc.height;
	var layer_width = layer_right - layer_left;
	var layer_height = layer_bottom - layer_top;
	if (layer_width == 0 || layer_height == 0)
		return;

	layer.copy();

	var tmpDoc = app.documents.add(layer_width, layer_height, 72, getLayerName(doc, layer), NewDocumentMode.RGB);
	app.activeDocument = tmpDoc;
	tmpDoc.paste();
	tmpDoc.layers[1].remove();
	tmpDoc.saveAs(new File(proj_root + "out/" + getLayerName(doc, layer)), new PNGSaveOptions());
	tmpDoc.close(SaveOptions.DONOTSAVECHANGES);

}

function dumpImages() {
	var doc = app.activeDocument;
	var layers = doc.layers;
	for (var i=0; i<layers.length; i++) {
		app.activeDocument = doc;
		var layer = layers[i];
		saveLayerImage(doc, layer);
	}
}

function test(i) {
	var doc = app.activeDocument;
	var layers = doc.layers;
	saveLayerImage(doc, layers[i]);
}

function main() {
	init();
	dumpImages();
	//test(0);
}

main();
