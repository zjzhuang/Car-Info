
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
  graph = JSON.stringify(req.body);
  console.log(graph);
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
