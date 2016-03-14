var express = require('express');    
var fs = require('fs');
var path = require('path')
var app = express();
app.use(express.static(path.join(__dirname, 'public')));

app.get('/hello/*', function(req, res){  
    console.log(req.query.name);  
    console.log(req.query.email);  
    res.send('Get Over');    
});

app.get('/', function(req, res){
	// console.log(req);
	fs.readFile(__dirname + "/index.html", 'utf8', function (err, data) {
       res.end(data);
   });
});

app.post('/visual', function(req, res){

	fs.readFile(__dirname + '/visual/visual.html', 'utf8', function(err, data) {
		// console.log(data);
		res.send(data);
	});
});

app.listen(8080);    
console.log('Listening on port 8080');  