
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , mysql = require('mysql')
  , partials = require('express-partials')

var app = module.exports = express.createServer();

// Configuration

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
  app.use(partials());
  app.use(express.static(__dirname + '/public'));
});

app.configure('development', function(){
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function(){
  app.use(express.errorHandler());
});

// get mysql running!
var client = mysql.createConnection({
  user: 'root',
  password: ''
});
client.connect();
client.query('show databases', function(err, res, fields) {
  if (err) { throw err; }
  // console.log(res);
});


// Routes

app.get('/', routes.index);

app.post('/visual', function(req, res){
  graph = {}
  graph["series"] = {
    "id":0,
    "name":req.body,
    "hot":54,
    "good":82,
    "bad":7,
    "neutual":11,
    "group":0
  };
  clinet.query('select * from tag where series=' + req.body, function(err, res, fields) {
    if (err) { 
      // return to 500 page.
      throw err; 
    }
    console.log(res);
    graph["nodes"] = [];
    tags = [""]
    node = {"id":1,"name":"","group":1,"weight":0};
    for tag in 
  });
  // graph = req.body;
  // graph = '{title: "test"}';
  // then we can access mysql to transform the value into json data.
  res.render('visual', {
    layout: '',
    graph: '{title: "test"}'
  });
});

app.listen(3000, function(){
  console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
});
