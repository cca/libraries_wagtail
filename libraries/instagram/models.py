from django.db import models


# neither a snippet nor a page, the data here is added via scheduled management cmd
class Instagram(models.Model):
    accessibility_caption = models.TextField(
        blank=True,
        help_text="Instagram's accessibility caption (AI-generated if we do not provide one)",
    )
    date_added = models.DateTimeField(auto_now=True, help_text="Date added to Wagtail")
    ig_id = models.TextField(blank=False, default="UNKNOWN")
    json = models.JSONField(
        blank=True, help_text="Raw JSON data from Instagram API", null=True
    )
    text = models.TextField(blank=True, help_text="Post caption")
    html = models.TextField(
        blank=True,
        help_text="Post caption with hashtags & usernames converted to <a> links",
    )
    # TODO instagram actually has image URLs longer than 500 characters
    image_url = models.URLField(
        blank=False, max_length=500, help_text="Image URL on Instagram"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        help_text="downloaded Instagram image",
    )
    # stackoverflow.com/questions/15470180/character-limit-on-instagram-usernames
    username = models.CharField(blank=False, max_length=30)

    def __str__(self):
        return self.text
