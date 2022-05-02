from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from wagtail.core.models import Page


# Custom validation for Page's clean() method to require search_description
# Used in several places, note you _MUST_ call super.clean() before this
# github.com/wagtail/wagtail/blob/master/wagtail/core/models.py#L437
def validate_clean(self):
    if not Page._slug_is_available(self.slug, self.get_parent(), self):
        raise ValidationError({'slug': _("This slug is already in use")})
    if self.search_description is None or self.search_description == '':
        raise ValidationError({'search_description': _("A Search Description is required.")})
