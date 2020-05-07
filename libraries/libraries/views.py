import csv
import io
import logging

from django.conf import settings
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag

from wagtail.core import hooks
from wagtail.documents import get_document_model
from wagtail.documents.models import document_served
from wagtail.documents.views.serve import document_etag
from wagtail.utils import sendfile_streaming_backend
from wagtail.utils.sendfile import sendfile

# logger specifically for tracking document downloads
logger = logging.getLogger('document')

@etag(document_etag)
@cache_control(max_age=3600, public=True)
def serve_wagtail_doc(request, document_id, document_filename):
    """
    Replacement for `wagtail.documents.views.serve`
    Substantial copying from original method:
    https://github.com/wagtail/wagtail/blob/master/wagtail/documents/views/serve.py
    Wagtail's default document view serves everything as an attachment.
    We'll bounce back to the URL and let the media server serve it.
    """
    # these first two passages copied from wagtail/documents/views/serve.py
    Document = get_document_model()
    doc = get_object_or_404(Document, id=document_id)

    # We want to ensure that the document filename provided in the URL matches
    # the one associated with the considered document_id. If not we can't be
    # sure that the document the user wants to access is the one corresponding
    # to the <document_id, document_filename> pair.
    if doc.filename != document_filename:
        raise Http404('This document does not match the given filename.')

    for fn in hooks.get_hooks('before_serve_document'):
        result = fn(doc, request)
        if isinstance(result, HttpResponse):
            return result

    # Send document_served signal & log
    document_served.send(sender=Document, instance=doc, request=request)
    # ensure log output is valid CSV
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([document_id, document_filename, request.headers['User-Agent']])
    logger.info(output.getvalue().strip())

    try:
        local_path = doc.file.path
    except NotImplementedError:
        local_path = None

    try:
        direct_url = doc.file.url
    except NotImplementedError:
        direct_url = None

    serve_method = getattr(settings, 'WAGTAILDOCS_SERVE_METHOD', None)

    # If no serve method has been specified, select an appropriate default for the storage backend:
    # redirect for remote storages (i.e. ones that provide a url but not a local path) and
    # serve_view for all other cases
    if serve_method is None:
        if direct_url and not local_path:
            serve_method = 'redirect'
        else:
            serve_method = 'serve_view'

    if serve_method in ('redirect', 'direct') and direct_url:
        # Serve the file by redirecting to the URL provided by the underlying storage;
        # this saves the cost of delivering the file via Python.
        # For serve_method == 'direct', this view should not normally be reached
        # (the document URL as used in links should point directly to the storage URL instead)
        # but we handle it as a redirect to provide sensible fallback /
        # backwards compatibility behaviour.
        return redirect(direct_url)

    if local_path:

        # Use wagtail.utils.sendfile to serve the file;
        # this provides support for mimetypes, if-modified-since and django-sendfile backends

        if hasattr(settings, 'SENDFILE_BACKEND'):
            return sendfile(request, local_path, attachment=False, attachment_filename=doc.filename)
        else:
            # Fallback to streaming backend if user hasn't specified SENDFILE_BACKEND
            return sendfile(
                request,
                local_path,
                attachment=False,
                attachment_filename=doc.filename,
                backend=sendfile_streaming_backend.sendfile
            )

    else:

        # We are using a storage backend which does not expose filesystem paths
        # (e.g. storages.backends.s3boto.S3BotoStorage) AND the developer has not allowed
        # redirecting to the file url directly.
        # Fall back on pre-sendfile behaviour of reading the file content and serving it
        # as a StreamingHttpResponse

        wrapper = FileWrapper(doc.file)
        response = StreamingHttpResponse(wrapper, content_type='application/octet-stream')

        # FIXME: storage backends are not guaranteed to implement 'size'
        response['Content-Length'] = doc.file.size

        return response
