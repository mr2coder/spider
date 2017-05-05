$(document).ready(function(){
   $("#add-set").click(function(){
  $("#btn_file").click()
  
}); 
    $("#btn_file").change(function(){
    var site=$("#btn_file").val();
    console.log("222"+site)
    if (site!="") 
        {window.open("http://10.108.219.219:5000/test","_blank","toolbar=yes, location=yes, directories=no, status=no, menubar=yes, scrollbars=yes, resizable=no, copyhistory=yes, width=400, height=400,left=400,top=200")};
            $("#btn_file").val("");
            });

 });


