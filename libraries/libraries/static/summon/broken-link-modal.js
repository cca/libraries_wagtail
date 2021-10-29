/* Credit to Robert Hoyt of Fairfield University who provided this code */
$(function() {
  // Modal HTML
  function modal(title, body, button) {
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
    </div><!-- /.modal -->`
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
                <label for="email" class="col-sm-2">Email</label>
                <div class="col-sm-10 col-sm-offset-1">
                    <input name="email" type="email" class="form-control">
                </div>
            </div>
            <div class="form-group">
                <label for="comments" class="col-sm-2">Comments</label>
                <div class="col-sm-10 col-sm-offset-1">
                    <textarea name="comments" class="form-control"></textarea>
                </div>
            </div>
            <input name="openurl" type="hidden" value="http://ey7mr5fu9x.search.serialssolutions.com?${doc.open_url}">
            <input name="permalink" type="hidden" value="https://cca.summon.serialssolutions.com/#!/search?bookMark=${doc.bookmark}">
            <input type="hidden" name="type" value="${doc.content_type}">
        </form>`
  }

  function addModal(doc) {
    let html = modal('Report Broken Link', prepareModalBody(doc), '<button type="button" class="btn btn-info submitBroken">Report Link</button>')
    $('.modal').remove()
    $('body').append(html)
    $('.modal').modal()
  }

  // run on loop, add "report broken link" to availability details for new docs
  function addReportLinks() {
      $('.documentSummary').each((i, el) => {
        let $item = $(el)
        if ($item.find('.reportBroken').length || $item.text().match('Find Similar')) {
          return
        }
        let doc = angular.element(el).scope().document
        // we used to check doc.content_type for "Journal" and not "Book" but this
        // didn't catch ebooks (e.g. Hathi Trust)
        if (doc && !doc.is_print && $item.find('.availabilityLink').text().match('Full Text Online')) {
          return $item.find('.fullText').append('<a class="availabilityLink reportBroken" href="#"><i class="uxf-icon uxf-alert"></i> Report Broken Link</a>')
        }
      })
  }

  // Open modal on click
  let modalLoaded = false
  $(document).on('click', '.reportBroken', function(e) {
    e.preventDefault()
    let doc = angular.element(e.currentTarget).parents('.ng-scope').scope().document
    if (!modalLoaded) {
      return $.getScript('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js').done(()=>{
        modalLoaded = true
        addModal(doc)
    }).fail(() => console.error('(BLR) Unable to load Bootstrap modal JS.'))
    }
    return addModal(doc)
  })

  // Handle submission of modal
  let sent = 0
  $(document).on('click', '.submitBroken', () => {
    if (sent === 1) return
    sent = 1
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
  }).done(() => {
      $('.modal-body').html('<div class="alert alert-success">Successfully Submitted</div>')
      setTimeout(() => $('.modal').modal('hide'), 3000)
  }).fail(() => {
      sent = 0
      alert('Could not submit.  Please Try again shortly.')
    })
  })

  // attach button to results in Summon, excluding books and journals
  let rootScope = angular.element('html').scope().$root
  rootScope.$on('apiSuccess', (scope) => setTimeout(addReportLinks, 500))
})
