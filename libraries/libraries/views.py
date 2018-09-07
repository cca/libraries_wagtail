from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from wagtail.documents.models import Document


def serve_wagtail_doc(request, document_id, document_filename):
    """
    Replacement for ``wagtail.documents.views.serve``
    Wagtail's default document view serves everything as an attachment.
    We'll bounce back to the URL and let the media server serve it.
    """
    doc = get_object_or_404(Document, id=document_id)
    return HttpResponseRedirect(doc.file.url)
