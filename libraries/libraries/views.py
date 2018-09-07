from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from wagtail.core import hooks
from wagtail.documents.models import document_served, get_document_model


def serve_wagtail_doc(request, document_id, document_filename):
    """
    Replacement for ``wagtail.documents.views.serve``
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

    # Send document_served signal
    document_served.send(sender=Document, instance=doc, request=request)
    return HttpResponseRedirect(doc.file.url)
