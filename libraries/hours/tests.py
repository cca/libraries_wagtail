import datetime

from categories.models.pages import CategoryPage, RowComponent
from django.urls import reverse
from libraries.tests.base import CMSPageTestCase, CMSSetupMixin
from libraries.tests.utils import PageFactory, create_test_image

from hours.models import (
    Closure,
    HoursPage,
    Library,
    OpenHours,
    get_hours_for_lib,
    get_open_hours,
)


class HoursAPITests(CMSPageTestCase, CMSSetupMixin):
    """Tests for the Hours API and related helpers."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Create standard page hierarchy for HoursPage
        cls.category_page = PageFactory.create_page(
            CategoryPage,
            parent=cls.home,
            title="About Us",
            search_description="About the Libraries",
            published=True,
        )

        cls.row = PageFactory.create_page(
            RowComponent,
            parent=cls.category_page,
            title="Hours & Locations",
            summary="<p>Visit us</p>",
            published=True,
        )

        cls.image = create_test_image(name="hours_api_test.png", size=(230, 115))

        cls.hours_page = PageFactory.create_page(
            HoursPage,
            parent=cls.row,
            title="Hours",
            intro="<p>Library hours</p>",
            main_image=cls.image,
            published=True,
        )

        # Create test Library models
        cls.meyer = Library.objects.create(name="Meyer")
        cls.simpson = Library.objects.create(name="Simpson")

        # Create typical open hours for Meyer
        # Active: 2026-06-01 to 2026-06-30
        cls.meyer_hours = OpenHours.objects.create(
            label="Meyer Summer 2026",
            library=cls.meyer,
            start_date=datetime.date(2026, 6, 1),
            end_date=datetime.date(2026, 6, 30),
            mon="9:00 AM - 5:00 PM",
            tue="9:00 AM - 5:00 PM",
            wed="9:00 AM - 5:00 PM",
            thu="9:00 AM - 5:00 PM",
            fri="9:00 AM - 5:00 PM",
            sat="closed",
            sun="closed",
        )

    def test_get_open_hours_typical_day(self):
        """Test get_open_hours for a day within the range."""
        # June 10, 2026 is a Wednesday
        day = datetime.date(2026, 6, 10)
        hours = get_open_hours(day)

        # Meyer should be open 9:00 AM - 5:00 PM (wed)
        self.assertEqual(hours["Meyer"], "9:00 AM - 5:00 PM")
        # Simpson has no open hours defined, should default to "closed"
        self.assertEqual(hours["Simpson"], "closed")

    def test_get_open_hours_closure_override(self):
        """Test that a Closure override sets the hours to closed."""
        # Create a closure for Meyer on Wednesday June 10, 2026
        closure = Closure.objects.create(
            label="Meyer Juneteenth",
            library=self.meyer,
            start_date=datetime.date(2026, 6, 10),
            end_date=datetime.date(2026, 6, 10),
            explanation="Closed for Juneteenth",
        )

        try:
            day = datetime.date(2026, 6, 10)
            hours = get_open_hours(day)

            # Meyer should now be closed due to the closure
            self.assertEqual(hours["Meyer"], "closed")
        finally:
            closure.delete()

    def test_get_open_hours_string_date_parsing(self):
        """Test that get_open_hours parses a string date in YYYY-MM-DD format."""
        # June 10, 2026 is a Wednesday
        hours = get_open_hours("2026-06-10")
        self.assertEqual(hours["Meyer"], "9:00 AM - 5:00 PM")

    def test_get_open_hours_invalid_string_date_fallback(self):
        """Test that get_open_hours defaults to today if string parsing fails."""
        # Pass invalid string date, should default to today.
        # Since today might not have hours defined, verify it doesn't crash.
        hours = get_open_hours("invalid-date")
        self.assertIsInstance(hours, dict)

    def test_get_hours_for_lib_valid(self):
        """Test get_hours_for_lib returns the correct weekday dict."""
        day = datetime.date(2026, 6, 10)
        hours = get_hours_for_lib("Meyer", day)

        self.assertIsNotNone(hours)
        self.assertEqual(hours["sat"], "closed")  # type: ignore

    def test_get_hours_for_lib_invalid(self):
        """Test get_hours_for_lib returns None if library has no hours."""
        day = datetime.date(2026, 6, 10)
        hours = get_hours_for_lib("Simpson", day)
        self.assertIsNone(hours)

    def test_hours_view_html_redirect(self):
        """Test that requests without format=json redirect to the HoursPage URL."""
        response = self.client.get(reverse("hours"))
        self.assertEqual(response.status_code, 302)
        # Should redirect to HoursPage url
        self.assertTrue(response.url.endswith(self.hours_page.url))

    def test_hours_view_json_success_single_library(self):
        """Test format=json with library parameter returns that library's hours."""
        response = self.client.get(
            reverse("hours"),
            {"format": "json", "library": "Meyer", "date": "2026-06-10"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["library"], "Meyer")
        self.assertEqual(data["hours"]["wed"], "9:00 AM - 5:00 PM")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_hours_view_json_success_all_libraries(self):
        """Test format=json with only date returns hours for all libraries."""
        response = self.client.get(
            reverse("hours"),
            {"format": "json", "date": "2026-06-10"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["Meyer"], "9:00 AM - 5:00 PM")
        self.assertEqual(data["Simpson"], "closed")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")

    def test_hours_view_json_invalid_library(self):
        """Test format=json with non-existent library returns 400 error."""
        response = self.client.get(
            reverse("hours"),
            {"format": "json", "library": "NonExistentLibrary"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("does not exist", data["error"])

    def test_hours_view_json_invalid_date(self):
        """Test format=json with invalid date returns 400 error."""
        response = self.client.get(
            reverse("hours"),
            {"format": "json", "date": "invalid-date-format"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("Unable to parse provided date string", data["error"])

    def test_hours_view_json_no_hours_found(self):
        """Test format=json when no hours are found for the library/date returns 400."""
        # July 10, 2026 is outside the start_date/end_date range of meyer_hours
        response = self.client.get(
            reverse("hours"),
            {"format": "json", "library": "Meyer", "date": "2026-07-10"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("No hours set found for library", data["error"])
