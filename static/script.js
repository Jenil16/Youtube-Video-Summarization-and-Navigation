var insertdetailsAPI = 'http://127.0.0.1:5000/insertdetails';
var signuploginform = document.getElementById('signuploginform')
var signupbtn = document.getElementById('signupbtn')

signupbtn.addEventListener('click', function () {
    // console.log('its working')
    let signuploginHTML = `  <div class="signup-login-form">
            <ul class="tab-group">
                <img src="close.png" alt="" width="25px" id="crossImg">
                <li class="tab active"><a href="#signup">Sign Up</a></li>
                <li class="tab"><a href="#login">Log In</a></li>
            </ul>
            <div class="tab-content">
                <div id="signup">
                    <h1>Sign Up for Free</h1>
                    <form id="signupform">
                        <div class="top-row">
                            <div class="field-wrap">
                                <label>
                                    Name<span class="req">*</span>
                                    </label>
                                <input type="text" required autocomplete="off" id="username" name="username" />
                            </div>
                            <div class="field-wrap">
                            <label>
                            Phone Number<span class="req">*</span>
                            </label>
                                <input type="tel" required autocomplete="off" id="usernumber" name="usernumber" />
                                </div>
                                </div>
                                <div class="field-wrap">
                                <label>
                                Email Address<span class="req">*</span>
                                </label>
                                <input type="email" required autocomplete="off" id="useremail" name="useremail" />
                        </div>
                        <div class="field-wrap">
                            <label>
                                Set A Password<span class="req">*</span>
                                </label>
                            <input type="password" required autocomplete="off" id="userpassword" name="userpassword" />
                            </div>
                        <button type="submit" class="button button-block" id="submitbtn">Submit</button>
                        </form>
                </div>
                <div id="login">
                <h1>Welcome Back!</h1>
                <form action="/" method="post">
                <div class="field-wrap">
                <label>
                Email Address<span class="req">*</span>
                </label>
                <input type="email" required autocomplete="off" />
                </div>
                <div class="field-wrap">
                <label>
                Password<span class="req">*</span>
                            </label>
                            <input type="password" required autocomplete="off" />
                        </div>
                        <p class="forgot"><a href="#">Forgot Password?</a></p>
                        <button class="button button-block">Log In</button>
                    </form>
                </div>
            </div>
        </div>`
    signuploginform.innerHTML = signuploginHTML
    var crossImg = document.getElementById('crossImg')
    crossImg.addEventListener('click', function () {
        signuploginform.innerHTML = ''
    })

    $('.signup-login-form').find('input, textarea').on('keyup blur focus', function (e) {

        var $this = $(this),
            label = $this.prev('label');
        if (e.type === 'keyup') {
            if ($this.val() === '') {
                label.removeClass('active highlight');
            } else {
                label.addClass('active highlight');
            }
        }
    });

    $('.tab a').on('click', function (e) {

        e.preventDefault();
        $(this).parent().addClass('active');
        $(this).parent().siblings().removeClass('active');
        target = $(this).attr('href');
        $('.tab-content > div').not(target).hide();
        $(target).fadeIn(600);

    });

    function callApi(method, url, data) {
        $.ajax({
            method: method,
            url: url,
            data: data
        }).done(function (msg) {
            console.log(msg)
        })
    }

    $('#submitbtn').on("click", function () {
        var data = $("#signupform").serializeArray();
        var requestPayload = {
            name: null,
            number: null,
            email: null,
            password: null
        };
        for (var i = 0; i < data.length; ++i) {
            var element = data[i];
            switch (element.name) {
                case 'username':
                    requestPayload.name = element.value;
                    break;
                case 'usernumber':
                    requestPayload.number = element.value;
                    break;
                case 'useremail':
                    requestPayload.email = element.value;
                    break;
                case 'userpassword':
                    requestPayload.password = element.value;
                    break;
            }
        }
        callApi("POST", insertdetailsAPI, {
            'data': JSON.stringify(requestPayload)
        });
    });
})



