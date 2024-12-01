from django.utils.translation import gettext as _
from rss_client.models import Feed, Tag
from chat.models import UserQuery
import openai
import json


# def test_internationalization():
    # it is used to test the internationalization
#     article = _("The Profound Benefits of Meditation: A Path to Wellness and Clarity Meditation, an ancient practice rooted in spiritual traditions, has gained widespread popularity in modern times as a powerful tool for mental, physical, and emotional well-being. This simple yet transformative practice involves focusing the mind to achieve a state of calm and heightened awareness. Whether practiced for a few minutes a day or as part of a more intensive routine, meditation offers a multitude of benefits that can positively impact every aspect of life.")
    
#     return article


def extrat_tags_from_question(question):
    """
    Generate tags for a given question by categorizing it into predefined categories.

    This function utilizes the OpenAI API to assign a given question to one or more 
    categories: 'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص'. The function returns a dictionary 
    with these categories as keys and lists of tags as values. It excludes countries and 
    cities from being classified as 'أشخاص'.

    Args:
        question (str): The question to be categorized.

    Returns:
        dict: A dictionary with the keys 'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص' and 
              their corresponding list of tags.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates keywords."},
        {"role": "user", "content": "assign the following question to one of the following categories without any signs or numbers and put a comma between , each tag"},
        {"role": "user", "content": "'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص'"},
        {"role": "user", "content": f"the question: {question}"},
        {"role": "user", "content": "(اقتصاد, فن, سياسة, أخبار, رياضة, تكنولوجيا, صحة) التصنيف العام يندرج تحته تلك العلامات"},
        {"role": "user", "content": "إليك مثال: السؤال: ما الجديد في حرب سوريا و غزه؟ "},
        {
            "role": "user",
            "content": "return as a python dict with the keys: 'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص' and the values as lists and dont write format of code"
        },
        {"role": "user", "content": "لا تضع الدول والمدن مثل الولايات المتحده و واشنطن وغيرها ضمن الاشخاص"},
        {
            "role": "user",
            "content": '{"تصنيف عام": ["أخبار"], "أماكن": ["سوريا، غزه"], "أحداث": ["حرب"], "أشخاص": []}'
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    keywords = response.choices[0].message['content'].strip()
    return keywords


def generate_response(feeds_titles, feeds_descriptions, question):
    """
    Generate a response to a given question based on a list of feeds titles and descriptions.

    The function utilizes the OpenAI API to generate a response to a given question based on a
    list of feeds titles and descriptions. The response is in Arabic language.

    Args:
        feeds_titles (list): A list of feeds titles.
        feeds_descriptions (list): A list of feeds descriptions.
        question (str): The question to be answered.

    Returns:
        str: The generated response.
    """
    titles_str = "\n".join(feeds_titles)
    descriptions_str = "\n".join(feeds_descriptions)

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Write an answer to the following question."},
        {"role": "user", "content": f"The question is: {question}"},
        {"role": "user", "content": "Generate an answer based on the following feeds."},
        {"role": "user", "content": f"The feed titles are:\n{titles_str}"},
        {"role": "user", "content": f"The feed descriptions are:\n{descriptions_str}"},
        {"role": "user", "content": "Answer in Arabic."},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    answer = response.choices[0].message['content'].strip()
    cleaned_response = answer.replace("\n", " ").strip()
    return cleaned_response


def ask_question(data: dict, request):
    """
    Process a question to generate a response based on related feeds and tags.

    This function extracts tags from the question, retrieves relevant feeds
    based on the tags and optional date range, and uses the OpenAI API to
    generate a response in Arabic. The response is saved to the database along
    with the question and associated tags.

    Args:
        data (dict): Input data containing the question and optional date range.
            - 'question' (str): The question to be processed.
            - 'date_range_start' (str, optional): The start date for filtering feeds.
            - 'date_range_end' (str, optional): The end date for filtering feeds.
        request: The HTTP request object containing user information.

    Returns:
        dict: A dictionary containing the success status, a message, and the generated response.
            - 'success' (bool): Indicates if the operation was successful.
            - 'message' (str): A message indicating the result of the operation.
            - 'payload' (str): The generated response or an error message if no feeds were found.
    """
    question: str = data['question']
    date_range_start: str = data.get('date_range_start')
    date_range_end: str = data.get('date_range_end')

    tags: json = extrat_tags_from_question(question)
    tags_dict: dict = json.loads(tags)
    categories: list = list(tags_dict.keys())
    tags: list = [tag for tags in tags_dict.values() for tag in tags]

    # Get tags and feeds from database
    tags = Tag.objects.filter(name__in=tags, category__name__in=categories).distinct()
    feeds_filters = {'tags__in': tags}
    if date_range_start:
        feeds_filters['created_at__date__gte'] = date_range_start
    if date_range_end:
        feeds_filters['created_at__date__lte'] = date_range_end
    if date_range_start and date_range_end:
        feeds_filters['created_at__date__range'] = (date_range_start, date_range_end)

    feeds = Feed.objects.filter(**feeds_filters).distinct()

    if not feeds:
        return {
            'success': False,
            'message': 'Be more specific, your question is not related to any feed or no feeds found in this date range',
            'payload': 'Be more specific, your question is not related to any feed or no feeds found in this date range'
        }

    # Send this feeds as a context to GPT
    feeds_titles = list(feeds.values_list('title', flat=True))
    feeds_descriptions = list(feeds.values_list('description', flat=True))

    # Generate response from GPT
    response = generate_response(feeds_titles, feeds_descriptions, question)

    # Save the response to the database
    UserQuery.objects.create(
        user=request.user,
        question=question,
        answer=response,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        tags=tags_dict
    )

    return {
        'success': True,
        'message': 'Feeds fetched successfully',
        'payload':  response
    }

    