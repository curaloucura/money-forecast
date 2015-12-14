/// Huge code dump for CSRF security
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  crossDomain: false, // obviates need for sameOrigin test
  beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
  }
});
/// End huge code dump

function prepareDatePicker(start_date, min_date, max_date){
    $('#id_start_date, #id_end_date').datetimepicker({
        format:'d.m.Y',
        formatDate:'d.m.Y',
        // allowTimes: ['07:00','12:00','18:00','22:00'], 
        // value: start_date, 
        startDate: start_date, 
        minDate: min_date, 
        maxDate: max_date, 
        timepicker: false, 
        validateOnBlur: false});
    $('#id_end_date').val('');
}


function prepareForm(start_date, min_date, max_date){
    prepareDatePicker(start_date, min_date, max_date);
    $('.modal-form').on('submit', function(){
        form = $(this);
        $.post(form.attr('action'), form.serialize(), function(responseText){
            if (responseText['id'] > 0){
                location.reload();
            } else {
                $('#record-form .modal-content').html(responseText);
            }
        });
        return false;
    }); 
    $('fieldset a.toggle').click(function(){
      var fieldset = $(this).parents('fieldset');
      fieldset.find('div.fields').toggle();
      $(this).find('span').toggleClass('glyphicon-collapse-down');
      $(this).find('span').toggleClass('glyphicon-collapse-up');
      return false;
    });
    var changeCategory = function() {
      var link = $('#add-category');
      var link_icon = link.find('span');
      var input_add = $('#add-new-category');
      var selector = $('#select-category');
      is_adding = input_add.is(':visible');
      if (is_adding) {
        input_add.hide();
        selector.show();
        link_icon.removeClass('glyphicon-remove');
        link_icon.addClass('glyphicon-plus');
        link.attr('title', link.data('title-add'));
      } else {
        selector.hide();
        input_add.show();
        link_icon.removeClass('glyphicon-plus');
        link_icon.addClass('glyphicon-remove');
        link.attr('title', link.data('title-cancel'));
        input_add.find('input').focus();
      };
      return false;
    }
    $('#add-category').click(changeCategory);
    $('#btn-calc').click(function(){
      var num_pay = parseInt($('#id_number_payments').val()) || 1; //if not valid number, returns 1
      var day_month = $('#id_day_of_month').val();
      var date = $('#id_start_date').val();
      var start = moment($('#id_start_date').val());
      if (!day_month){
        day_month = start.date();
        $('#id_day_of_month').val(day_month);
      }
      var final_date = start.date(day_month);
      var final_date = final_date.add(num_pay, 'months');
      $('#id_end_date').val(final_date.format('YYYY/MM/DD HH:mm'))
    });
}
