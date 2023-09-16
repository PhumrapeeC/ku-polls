from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect
from .models import Choice, Question


class IndexView(generic.ListView):
    """
    View to display a list of the latest published questions.

    Attributes:
        template_name (str): The name of the template to be used for rendering the view.
        context_object_name (str): The name of the context variable to store the queryset.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    View to display the details of a specific question.

    Attributes:
        model (Question): The model associated with this view.
        template_name (str): The name of the template to be used for rendering the view.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Return the questions that are published and not in the future.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, **kwargs):
        """
        Handle GET requests for the detail view.

        Checks if the question is published and allows voting.
        If not published or voting is not allowed, redirects to the index page with an error message.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The HTTP response.
        """
        try:
            self.object = self.get_object()
        except Http404:
            # Handle the case where the object is not found
            messages.error(request, "Poll not found.")
            return redirect('polls:index')

        if not self.object.is_published():
            messages.error(request, "This question is not published yet.")
            return redirect('polls:index')

        if not self.object.can_vote():
            messages.error(request, "Voting for this poll is not allowed.")
            return redirect('polls:index')

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ResultsView(generic.DetailView):
    """
    View to display the results of a specific question.

    Attributes:
        model (Question): The model associated with this view.
        template_name (str): The name of the template to be used for rendering the view.
    """
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        context['choices'] = question.choice_set.all()
        return context


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        messages.error(request, "Voting for this poll is not allowed.")
        return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    # Remove all of the user's previous votes (for all questions)
    request.user.voted_choices.clear()

    # Add the new vote
    selected_choice.votes.add(request.user)

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
