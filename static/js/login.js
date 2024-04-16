var signuploginform = document.getElementById("signuploginform");
var signupbtn = document.getElementById("signupbtn");


$(".signup-login-form")
    .find("input, textarea")
    .on("keyup blur focus", function (e) {
      var $this = $(this),
        label = $this.prev("label");
      if (e.type === "keyup") {
        if ($this.val() === "") {
          label.removeClass("active highlight");
        } else {
          label.addClass("active highlight");
        }
      }
    });

  $(".tab a").on("click", function (e) {
    e.preventDefault();
    $(this).parent().addClass("active");
    $(this).parent().siblings().removeClass("active");
    target = $(this).attr("href");
    $(".tab-content > div").not(target).hide();
    $(target).fadeIn(600);
  });

 
