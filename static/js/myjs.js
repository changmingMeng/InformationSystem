function page_click(buttonId){
  var current_page = parseInt($(".count").text());
  //alert(buttonId, current_page)
  if(buttonId == "pre"){
      if(current_page > 1){
        var page = current_page -1;
        $(".count").text(page);
        page_click_implement(page);
      }
  }
  else if (buttonId == "next") {
      if(current_page < $("#foot_pages").children("#page_button").length){
        var page = current_page + 1;
        $(".count").text(page);
        page_click_implement(page);
      }
  }
  else {
    $(".count").text(buttonId);
    page_click_implement(buttonId)
  }
}

function page_click_implement(buttonId){
  //alert(buttonId)
  $("tbody").children().hide();
  var len = $("tbody").children().length;
  for(var i = (buttonId-1)*10; i < len && i < buttonId*10; i++){
    $("tbody").children().eq(i).show();
  }

  $("#foot_pages").children("#page_button").attr("class", "item");
  $("#foot_pages").children("#page_button").eq(buttonId-1).attr("class", "item active")
}
