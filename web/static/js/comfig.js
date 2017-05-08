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
      day = $("#day").find("option:selected").text();
      week = $("#week").find("option:selected").text();
      hour = $("#hour").find("option:selected").text();
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
    function config()
    {
      
      console.log("11111111111111")
       $.post('/config_set', {
        },function(responseTxt){
        var str = responseTxt.split('\n');
        $.each(str,function(i,val)
              {
                
                if(i==1)
                  {
                    console.log(val)
                   // $('#day option').filter(function(){return $(this).text()=="7";}).attr("selected",true);
                   var count=$("#day").get(0).options.length;  
            for(var i=0;i<count;i++){  
              if($("#day").get(0).options[i].text == "8")    
              {  
                $("#day").get(0).options[i].selected = true;            
                break;    
              }    
            } 
                  }
                  if(i==3)
                  {
                    console.log(val)
                    $("#week option:contains('周四')").attr('selected', true);
                  }
                   if(i==5)
                  {
                    console.log(val)
                    $("#hour option:contains('4')").attr('selected', true);
                  }
                   if(i==7)
                  {
                    console.log(val)
                    $("#site").val(val);
                  }
              });
       });
       console.log("2222222222222222222")
    }
 });


