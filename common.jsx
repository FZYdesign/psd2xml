
proj_root = "/Users/linyun/Documents/ws-test/psd2xml/";

function init() {
	app.preferences.typeUnits = TypeUnits.POINTS;
	app.preferences.rulerUnits = Units.POINTS;
}

function filterName(name) {
	return name.replace(new RegExp("[^_a-zA-Z0-9]", "g"), "_");
}

function dumpDoc(func, doc) {
	prefix = doc.name.replace('.psd', '');
	for (var i=0; i<doc.artLayers.length; i++) {
		dumpArtLayer(func, doc, doc.artLayers[i], prefix + '_artlayer' + i);
	}
	for (var i=0; i<doc.layerSets.length; i++) {
		dumpLayerSet(func, doc, doc.layerSets[i], prefix + '_layerset' + i, 1);
	}
}

function dumpLayerSet(func, doc, layerSet, prefix, deep) {
	if (!layerSet.visible)
		return;
	if (deep == 2) {
		var len = layerSet.layerSets.length;
		for (var i=0; i<len; i++)
			layerSet.layerSets[0].merge();
	}
	for (var i=0; i<layerSet.artLayers.length; i++) {
		dumpArtLayer(func, doc, layerSet.artLayers[i], prefix + '_artlayer' + i);
	}
	for (var i=0; i<layerSet.layerSets.length; i++) {
		dumpLayerSet(func, doc, layerSet.layerSets[i], prefix + '_layerset' + i, deep + 1);
	}
}

function dumpArtLayer(func, doc, artLayer, prefix) {
	if (!artLayer.visible)
		return;
	if (artLayer.isBackgroundLayer)
		return;
	if (artLayer.kind == LayerKind.BRIGHTNESSCONTRAST)
		artLayer = artLayer.merge();
	else if (artLayer.kind == LayerKind.SOLIDFILL || artLayer.kind == LayerKind.SMARTOBJECT)
		artLayer.rasterize(RasterizeType.ENTIRELAYER);

	var left = artLayer.bounds[0] > 0 ? artLayer.bounds[0] : 0;
	var ttop = artLayer.bounds[1] > 0 ? artLayer.bounds[1] : 0;
	var right = artLayer.bounds[2] < doc.width ? artLayer.bounds[2] : doc.width;
	var bottom = artLayer.bounds[3] < doc.height ? artLayer.bounds[3] : doc.height;
	var width = right - left;
	var height = bottom - ttop;
	if (width == 0 || height == 0)
		return;

	artLayer.bounds = [left, ttop, right, bottom];
	artLayer.width = width;
	artLayer.height = height;

	func(doc, artLayer, prefix);
}

