// @include 'json.jsx'
// @include 'common.jsx'

layersInfo = []
function getLayerInfo(doc, layer, prefix) {
	bounds = [];
	for (var i=0; i<layer.bounds.length; i++)
		bounds.push(layer.bounds[i].value);
	filename = [prefix, layer.name].join('_');
	filename = filterName(filename)
	info = {
		name : filename,
		bounds : bounds,
		kind : layer.kind
	}
	return layersInfo.push(info);
}

function main() {
	init();
	var doc = app.activeDocument;
	dumpDoc(getLayerInfo, doc);

	docInfo = {}
	docInfo.width = doc.width.value;
	docInfo.height = doc.height.value;
	docInfo.layersInfo = layersInfo;

	var file = File(proj_root + "out/layers.txt");
	file.open("e", "TEXT", "????");
	file.writeln(JSON.stringify(docInfo));
	file.close();

	alert("OK");
}

main()

