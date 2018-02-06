/* Credit to Robert Hoyt of Fairfield University who provided this code */
$(function() {
  var modalLoaded = false;

  // Modal HTML
  var modal = function (title, body, button) {
    return `<div class="modal fade" tabindex="-1" role="dialog">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h4 class="modal-title">${title}</h4>
            </div>
            <div class="modal-body" id="modal-body">
                ${body}
                <div class="results"></div>
            </div>
            <div class="modal-footer">
                ${button}
                <button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>
            </div>
          </div><!-- /.modal-content -->
        </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->`;
  }

  // Modal Content
  function prepareModalBody(doc) {
    return `<p>This submission may take some time to process. If you need help immediately, please use the "Help" link at the top right.
        <p>Please leave your email if you wish to be informed about the progress on this resource.</p>
        <hr/>
        <form id="brokenForm" class="form-horizontal">${doc.title}
            <br/>by ${doc.authors.map((a) => a.fullname).join('; ')}
            <br/>Content Type: ${doc.content_type}
            <hr/>
            <div class="form-group">
                <label for="email" class="col-sm-2">E-mail</label>
                <div class="col-sm-10">
                    <input name="email" type="email" class="form-control" style="height:34px;">
                </div>
            </div>
            <div class="form-group">
                <label for="comments" class="col-sm-2">Comments</label>
                <div class="col-sm-10">
                    <textarea name="comments" class="form-control" style="max-width:100%"></textarea>
                </div>
            </div>
            <input name="openurl" type="hidden" value="http://ey7mr5fu9x.search.serialssolutions.com?${doc.open_url}">
            <input name="permalink" type="hidden" value="https://cca.summon.serialssolutions.com/#!/search?bookMark=${doc.bookmark}">
            <input type="hidden" name="type" value="${doc.content_type}">
        </form>`;
  }

  //Open modal on click
  $(document).on('click', '.reportBroken', function(e) {
    e.preventDefault();
    var doc = angular.element(e.currentTarget).parents('.ng-scope').scope().doc;
    function addModal() {
      var html = modal('Report Broken Link', prepareModalBody(doc), '<button type="button" class="btn btn-info submitBroken">Report Link</button>');
      $('.modal').remove();
      $('body').append(html);
      $('.modal').modal();
    }
    if (!modalLoaded) {
      $.getScript('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js').done(function() {
        modalLoaded = true;
        addModal()
      });
    } else {
      addModal();
    }
  });

  //Handle submission of modal
  var sent = 0;
  $(document).on('click', '.submitBroken', function() {
    if (sent === 1) {
      return false;
    }
    sent = 1;
    // NOTE: this is being sent as POST body content, not JSON, for some reason
    $.ajax({
      headers: {'Accept': 'application/json', 'Content-Type': 'application/json; charset=utf-8'},
      url: 'https://libraries.cca.edu/brokenlinks/',
      method: 'POST',
      data: {
          'openurl': $('#brokenForm input[name="openurl"]').val(),
          'permalink': $('#brokenForm input[name="permalink"]').val(),
          'email': $('#brokenForm input[name="email"]').val(),
          'type': $('#brokenForm input[name="type"]').val(),
          'comments': $('#brokenForm textarea[name="comments"]').val(),
      }
    }).done(function(d) {
      $('.modal-body').html('<div class="alert alert-success">Successfully Submitted</div>');
      setTimeout(function() {$('.modal').modal('hide');}, 3000);
    }).fail(function(d) {
      sent = 0;
      alert('Could not submit.  Please Try again shortly.');
    });
  });

  // attach button to results in Summon, excluding books and journals
  var mainMod = angular.module('summonApp');
  var rootScope = angular.element('html').scope().$root;
  rootScope.$on('apiSuccess',
    function(scope, type) {
      setTimeout(function() {
        // broken link button
        $('.Z3988').parent().each(function() {
          if ($(this).text().indexOf('Report Broken') !== -1
          || $(this).text().indexOf('Find Similar') !== -1) {
            return;
          }
          var doc = angular.element(this).scope().doc;
          var type = doc.content_type;
          if (doc && type !== 'Book' && type !== 'Journal' && !doc.is_print) {
            $(this).append('<span class="availability" style="margin-left:15px"><a class="availabilityLink reportBroken" href="#"><i class="fa fa-exclamation-triangle fa-fw"></i> Report Broken Link</a></span>');
          }
        });
      });
    }
  );
});
