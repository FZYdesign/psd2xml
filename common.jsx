
proj_root = "/Users/linyun/Documents/ws-test/psd2xml/";

function init() {
	app.preferences.typeUnits = TypeUnits.POINTS;
	app.preferences.rulerUnits = Units.POINTS;
}

function getLayerName(doc, layer) {
	var layer_name = doc.name.replace(".psd", "") + "_" + layer.name.replace(new RegExp("[^_a-zA-Z0-9]", "g"), "_");
	return layer_name;
}

function dumpDoc(func, doc) {
	prefix = doc.name.replace('.psd', '');
	for (var i=0; i<doc.artLayers.length; i++)
		dumpArtLayer(func, doc, doc.artLayers[i], prefix);
	for (var i=0; i<doc.layerSets.length; i++)
		dumpLayerSet(func, doc, doc.layerSets[i], prefix, 1);
}

function dumpLayerSet(func, doc, layerSet, prefix, deep) {
	if (!layerSet.visible)
		return;
	if (deep == 2) {
		dumpArtLayer(func, doc, layerSet.merge(), prefix);
	} else {
		prefix = [prefix, layerSet.name].join('_');
		for (var i=0; i<layerSet.artLayers.length; i++)
			dumpArtLayer(func, doc, layerSet.artLayers[i], prefix);
		for (var i=0; i<layerSet.layerSets.length; i++)
			dumpLayerSet(func, doc, layerSet.layerSets[i], prefix, deep + 1);
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
	func(doc, artLayer, prefix);
}

