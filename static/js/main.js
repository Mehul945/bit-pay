document.getElementById("receivebitcoin").style.display = "none";
document.getElementById("sendbitcoin").style.display = "none";
document.getElementById("pk").style.display = "none";
function receiveFunction() {
    var x = document.getElementById("receivebitcoin");
    var y = document.getElementById("details");
    var z = document.getElementById("sendbitcoin")
    var pk = document.getElementById("pk")
    if (x.style.display === "none") {
    z.style.display = "none";
    y.style.display = "none";
    x.style.display = "block";
    } else {
    z.style.display = "none";
    x.style.display = "none";
    y.style.display = "block";
    }
}
function sendFunction() {
    var x = document.getElementById("receivebitcoin");
    var y = document.getElementById("details");
    var z = document.getElementById("sendbitcoin")
    if (z.style.display === "none") {
    z.style.display = "block";
    y.style.display = "none";
    x.style.display = "none";
    } else {
    z.style.display = "none";
    x.style.display = "none";
    y.style.display = "block";
    }
}
function getpk(){
    pk.style.display = "block";
}


(function ($) {
    "use strict";

    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    
    /*==================================================================
    [ Show pass ]*/
    var showPass = 0;
    $('.btn-show-pass').on('click', function(){
        if(showPass == 0) {
            $(this).next('input').attr('type','text');
            $(this).find('i').removeClass('fa-eye');
            $(this).find('i').addClass('fa-eye-slash');
            showPass = 1;
        }
        else {
            $(this).next('input').attr('type','password');
            $(this).find('i').removeClass('fa-eye-slash');
            $(this).find('i').addClass('fa-eye');
            showPass = 0;
        }
        
    });

})(jQuery);