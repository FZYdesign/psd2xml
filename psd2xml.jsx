
function main() {
	var file = File('/Users/linyun/Documents/Android-UI/home.psd');
	var doc = app.open(file);
	var layers = doc.layers;
		//app.activeDocument.crop();

	alertLayers(layers);
}

function alertLayers(layers) {
	var text = 'layers: ' + layers.length + '\n\n';
	for (var i=0; i<layers.length; i++) {
		l = layers[i];
		text += l.name + ':\n'
			+ l.bounds + '\n';
		if (l instanceof ArtLayer)
			text += 'ArtLayer\n';
		else if (l instanceof LayerSet)
			text += 'LayerSet\n';
		text += '\n';
	}
	var file = File("/Users/linyun/Documents/ws-test/photoshop/tmp.txt");
	file.open("e", "TEXT", "????");
	file.writeln(text);
	file.close();
	alert("OK");
}

main()
