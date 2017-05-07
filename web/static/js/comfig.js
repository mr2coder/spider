$(document).ready(function(){
    $("#add-set").click(function(){
  $("#btn_file").click()
  
}); 
    $("#btn_file").change(function(){
    var site=$("#btn_file").val();
    console.log("222"+site)
    if (site!="") 
        {window.open("http://localhost/test","_blank","toolbar=no, location=yes, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=yes, width=400, height=400,left=400,top=200")};
            $("#btn_file").val("");
            });
    $("#add").click(function(){
      day = $('select[name="day"]').val();
      week = $('select[name="week"]').val();
      hour = $('select[name="hour"]').val();
      site = $('input[name="site"]').val();
          $.post('/congif_file', {
            day:day,
            week:week,
            hour:hour,
            site:site
        })
          console.log("nihao")
    })

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


