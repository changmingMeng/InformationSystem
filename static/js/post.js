function post(URL, PARAMS) {
  var temp = document.createElement("form");
  temp.action = URL;
  temp.method = "post";
  temp.style.display = "none";
  for (var x in PARAMS) {
    var opt = document.createElement("textarea");
    opt.name = x;
    opt.value = PARAMS[x];
    // alert(opt.name)
    temp.appendChild(opt);
  }
  document.body.appendChild(temp);
  temp.submit();
  return temp;
}

function sendpost(){
    $("#querybutton").click(function(){
        $.post("select",
        {
          name:$("#cellname").val(),
          type:$("#celltype").val(),
          date:$("#date").val()
        });//,
        // function(data,status){
        //   alert($("#cellname").val() + "\n：" + $("#celltype").val());
        // })
    });