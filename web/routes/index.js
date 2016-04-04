
/*
 * GET home page.
 */

exports.index = function(req, res){
	res.render('index', {layout: '', title: 'test'});
};
// exports.visual = function(req, res){
// 	res.render('visual', graph);
// };	