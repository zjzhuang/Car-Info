var express = require('express');    
var app = express();   

app.get('/hello/*', function(req, res){  
    console.log(req.query.name);  
    console.log(req.query.email);  
    res.send('Get Over');    
});    
  
app.get('/', function(req, res){  
res.render('index');  
});  
  
app.listen(8080);    
console.log('Listening on port 8080'); 