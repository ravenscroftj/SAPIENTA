
var LOADERIMAGE = "<img src=\"/static/ajaxload.gif\" alt=\"Refreshing...\">";

$(document).ready(function(){
	
	var TestController = {
			
			socketns: '/sapienta',
			socket: null,
			testPapers: [],
			
			
			
			refreshPapers: function(){
				var _self = this;
				
				$("#foundPapersTotal").html(LOADERIMAGE);
				
				$.get("/refresh_papers", function(data){
					$("#foundPapersTotal").html(data.papers.length);
					_self.testPapers = data.papers;
					var table = $('#paperTable').dataTable().api();
					
					table.clear().rows.add(data.papers).draw();
					
				});
				
			},	
			
			inspect: function(paperid){
				location.hash = "#inspector";
				
				$("#paperInspectorTableTitle").html(paperid);
				
				$("#paperInspectorTable tbody").html("<tr><td colspan=\"5\">" + LOADERIMAGE + "</td></tr>");
				
				
				TestController.socket.emit('inspect-paper', paperid);
				
			},
			
			startConnection: function(){
				
				var _self = this;
				
				this.socket = io.connect("http://" + document.domain + ':' + location.port + this.socketns);

				this.socket.on("paper_updated", function(paper) {
					var table = $('#paperTable').dataTable().api();
					
					table.row(function(idx,data,node){
						if(data.paper_id == paper.paper_id) {
							return true;
						}
					}).data(paper).draw();
					
				});
				
				this.socket.on("test_finished", function(data){
					$("#runTestBtn").removeAttr("disabled");
					$("#overallPercent").html(data.totalpercent)
				});
				
				this.socket.on('paper-inspect-result', function(data) {
					
					$("#paperInspectorTable tbody").html("");
					
					var limit = Math.min( data.auto.length, data.manual.length );
					
					for(var i=0; i < limit; i++) {
						
						var man  = data.manual[i];
						var auto = data.auto[i];
						var row_class = "danger";
						
						if(man.first == auto.first && man.last == auto.last) {
							row_class = "success"
						}
						
						$("#paperInspectorTable tbody").append("<tr class=\"" + row_class + "\">"+
								"<td>" + (i+1) + "</td>" +
								"<td>" + man.first + "</td>" +
								"<td>" + man.last  + "</td>" +
								"<td>" + auto.first + "</td>" + 
								"<td>" + auto.last  + "</td></tr>");
						
					}
				});
			},
			
			runTest: function(){
				var _self = this;
				this.disabled = true;
				TestController.socket.emit('runsplitter')
			}
			
	};
	
	
	
	
	$("#corpusRescanBtn").click(TestController.refreshPapers);
	$("#runTestBtn").click(TestController.runTest);
	
	TestController.refreshPapers();
	
	TestController.startConnection();
	
	$('#paperTable').dataTable({
		data: TestController.testPapers,
		columns: [
		   { "data" : "name" },
		   { "data" : "manual_sents"},
		   { "data" : "auto_sents"},
		   { "data" : "sssplit_sents"},
		   { "data" : "match"}
		]
		
	});
	
	$("#paperTable").on( 'draw.dt', function(){
		
		$("#paperTable tr").unbind('click').click(function(){
			var row = $('#paperTable').dataTable().api().row(this);
			TestController.inspect(row.data().paper_id)
		});
	});
	
});



