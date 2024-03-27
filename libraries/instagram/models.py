from django.db import models


# neither a snippet nor a page, the data here is added via scheduled management cmd
class Instagram(models.Model):
    date_added = models.DateTimeField(auto_now=True)
    ig_id = models.TextField(blank=False, default="UNKNOWN")
    text = models.TextField(blank=True)
    html = models.TextField(
        blank=True,
        help_text="Text of gram with hashtags & usernames converted to <a> links",
    )
    # TODO instagram actually has image URLs longer than 500 characters
    image_url = models.URLField(blank=False, max_length=500)
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


class InstagramOAuthToken(models.Model):
    date_added = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=300)

    def __str__(self):
        return self.token
