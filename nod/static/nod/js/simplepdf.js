function exportpdf(rep_tag){
        var pdf = new jsPDF();
        // pdf.text(30, 30, 'Hello world!');

		// We'll make our own renderer to skip this editor
		var specialElementHandlers = {
		'body': function(element, renderer){
		return true;
		}
		};
	
		// All units are in the set measurement for the document
		// This can be changed to "pt" (points), "mm" (Default), "cm", "in"
		pdf.fromHTML($(rep_tag).get(0), 15, 15, {
		'width': 170, 
		'elementHandlers': specialElementHandlers
		});
        pdf.save('hello_world.pdf');
    }
