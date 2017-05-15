$(document).ready(function(){
    $("#add-set").click(function(){
  $("#btn_file").click()
  
}); 
 /*   $("#btn_file").change(function(){
    var site=$("#btn_file").val();
    console.log("yxj222"+site)
   $.post('/open_file', {
            site:site
        },function(responseTxt){
        var strHTML="";
        var str = responseTxt.split('\n');
        $.each(str,function(i,val)
              {
                  strHTML+=val+'<br>';
              });
        $("#logsite").html(strHTML);
        $("#siteModal").modal('show')
          console.log("nihao")
    })
 })*/


   $("#add_note").click(function(){
   	console.log("hgfgffhg")
    	time = $('input[name="time"]').val();
        note = $('select[name="note"]').val();

       console.log(time)
         $.post('/check_note', {
            time:time,
            note:note
        },function(responseTxt){
        var strHTML="";
        var str = responseTxt.split('\n');
        $.each(str,function(i,val)
              {
                  strHTML+=val+'<br>';
              });
        $("#log").html(strHTML);
        $("#paperModal").modal('show')
       });
    });
    
 });
function upload(input) {
  //支持chrome IE10
  if (window.FileReader) {
    var file = input.files[0];
    filename = file.name.split(".")[0];
    var reader = new FileReader();
    reader.onload = function() {
      console.log(this.result)
      //alert(this.result);
      response=this.result;
      console.log(response);
      var strHTML="";
        var str = response.split('\n');
        $.each(str,function(i,val)
              {
                  strHTML+=val+'<br>';
              });
         $("#logsite").html(strHTML);
        $("#siteModal").modal('show')
          console.log("nihao")
    }
    reader.readAsText(file);
  } 
  //支持IE 7 8 9 10
  else if (typeof window.ActiveXObject != 'undefined'){
    var xmlDoc; 
    xmlDoc = new ActiveXObject("Microsoft.XMLDOM"); 
    xmlDoc.async = false; 
    xmlDoc.load(input.value); 
    alert(xmlDoc.xml); 
  } 
  //支持FF
  else if (document.implementation && document.implementation.createDocument) { 
    var xmlDoc; 
    xmlDoc = document.implementation.createDocument("", "", null); 
    xmlDoc.async = false; 
    xmlDoc.load(input.value); 
    alert(xmlDoc.xml);
  } else { 
    alert('error'); 
  } 
}

