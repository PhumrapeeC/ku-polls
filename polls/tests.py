import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )
    
    def test_is_published_with_future_pub_date(self):
        """
        is_published() should return False for a question with a future pub date
        """
        future_question = create_question(question_text='Future question.', days=5)
        self.assertIs(future_question.is_published(), False)
    
    def test_is_published_with_default_pub_date(self):
        """
        is_published() should return True for a question with the default pub date (now)
        """
        default_question = create_question(question_text='Default question.', days=0)
        self.assertIs(default_question.is_published(), True)
    
    def test_is_published_with_past_pub_date(self):
        """
        is_published() should return True for a question with a pub date in the past
        """
        past_question = create_question(question_text='Past question.', days=-5)
        self.assertIs(past_question.is_published(), True)
    
    def test_can_vote_with_future_end_date(self):
        """
        Test that can_vote returns True when the end_date is in the future.
        """
        future_date = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=timezone.now(), end_date=future_date)
        self.assertIs(question.can_vote(), True)
    
    def test_can_vote_with_past_end_date(self):
        """
        Test that can_vote returns False when the end_date is in the past.
        """
        past_date = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=timezone.now(), end_date=past_date)
        self.assertIs(question.can_vote(), False)
    
    def test_can_vote_with_no_end_date(self):
        """
        Test that can_vote returns True when there is no end_date set.
        """
        question = Question(pub_date=timezone.now(), end_date=None)
        self.assertIs(question.can_vote(), True)

    def test_can_vote_with_current_date_as_end_date(self):
        """
        Test that can_vote returns True when the end_date is set to the current date.
        """
        current_date = timezone.now()
        question = Question(pub_date=timezone.now(), end_date=current_date)
        self.assertFalse(question.can_vote())