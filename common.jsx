
proj_root = "/Users/linyun/Documents/ws-test/psd2xml/";

function init() {
	app.preferences.typeUnits = TypeUnits.POINTS;
	app.preferences.rulerUnits = Units.POINTS;
}

function getLayerName(doc, layer) {
	var layer_name = doc.name.replace(".psd", "") + "_" + layer.name.replace(new RegExp("[^_a-zA-Z0-9]", "g"), "_");
	return layer_name;
}

function filterLayer(layer) {
	if (!layer.visible || layer.isBackgroundLayer)
		return false;

	if (layer.kind == LayerKind.BRIGHTNESSCONTRAST || layer.kind == undefined)
		layer = layer.merge();
	else if (layer.kind == LayerKind.SOLIDFILL || layer.kind == LayerKind.SMARTOBJECT)
		layer.rasterize(RasterizeType.ENTIRELAYER);
	return true;
}

