from django.utils.translation import gettext as _
from rss_client.models import Feed, Tag
from chat.models import UserQuery
import openai
from rapidfuzz import process, fuzz
import json
from django.conf import settings
import openai
from pgvector.django import CosineDistance

# def test_internationalization():
# it is used to test the internationalization
#     article = _("The Profound Benefits of Meditation: A Path to Wellness and Clarity Meditation, an ancient practice rooted in spiritual traditions, has gained widespread popularity in modern times as a powerful tool for mental, physical, and emotional well-being. This simple yet transformative practice involves focusing the mind to achieve a state of calm and heightened awareness. Whether practiced for a few minutes a day or as part of a more intensive routine, meditation offers a multitude of benefits that can positively impact every aspect of life.")

#     return article


def get_similar_tags(tags):
    """Fetch tags from the database with similar names using fuzzy matching."""
    all_db_tags = Tag.objects.values_list("name", flat=True)
    similar_tags = set()

    for tag in tags:
        matched_tags = [
            match[0]  # Unpack only the matched tag name
            for match in process.extract(tag, all_db_tags, scorer=fuzz.partial_ratio)
            if match[1] > 35  # Check if the score is above the threshold
        ]
        similar_tags.update(matched_tags)

    return list(similar_tags)

def get_best_matched_feeds(question,user_id, date_range_start=None, date_range_end=None, k=10):
    embedding = get_embeddings(question)
    feeds_query = {}
    if date_range_start:
        feeds_query["created_at__date__gte"] = date_range_start
    if date_range_end:
        feeds_query["created_at__date__lte"] = date_range_end
    
    objects =Feed.objects.filter(user_id=user_id).annotate(distance=CosineDistance("embedding", embedding)).order_by("distance")
    if objects.count() < 1:
        return None
    if objects.count() < k:
        return objects
    return objects[:k]


    
    
def get_embeddings(text):
    """
    Generate embeddings for a given text using the OpenAI API.

    This function utilizes the OpenAI API to generate embeddings for a given text.
    The embeddings are returned as a list of floats.

    Args:
        text (str): The text for which embeddings are to be generated.

    Returns:
        list: A list of floats representing the embeddings for the given text.
    """
    model= settings.OPENAI_EMBEDDING_MODEL
    base_url = settings.OPENAI_API_BASE_URL
    api_key = settings.OPENAI_API_KEY
    openai.api_key = api_key
    openai.api_base = base_url
    response = openai.Embed.create(model=model, objects=[{"text": text}])
    if "error" in response:
        raise Exception(response["error"]["message"])
    embeddings = response["embedding"]
    return embeddings


def extrat_tags_from_question(question):
    """
    Generate tags for a given question by categorizing it into predefined categories.

    This function utilizes the OpenAI API to assign a given question to one or more
    categories:  'أماكن', 'أحداث', 'أشخاص'. The function returns a dictionary
    with these categories as keys and lists of tags as values. It excludes countries and
    cities from being classified as 'أشخاص'.

    Args:
        question (str): The question to be categorized.

    Returns:
        dict: A dictionary with the keys  'أماكن', 'أحداث', 'أشخاص' and
              their corresponding list of tags.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that generates keywords.",
        },
        {
            "role": "user",
            "content": "assign the following question to one of the following categories without any signs or numbers and put a comma between , each tag",
        },
        {"role": "user", "content": " 'أماكن', 'أحداث', 'أشخاص'"},
        {"role": "user", "content": f"the question: {question}"},
        {
            "role": "user",
            "content": "إليك مثال: السؤال: ما الجديد في حرب سوريا و غزه؟ ",
        },
        {
            "role": "user",
            "content": "return as a python dict with the keys:  'أماكن', 'أحداث', 'أشخاص' and the values as lists and dont write format of code",
        },
        {
            "role": "user",
            "content": "لا تضع الدول والمدن مثل الولايات المتحده و واشنطن وغيرها ضمن الاشخاص",
        },
        {
            "role": "user",
            "content": '{"أماكن": ["سوريا، غزه"], "أحداث": ["حرب"], "أشخاص": []} مثال:',
        },
        {
            "role": "user",
            "content": "Dont add 'أخبار' in the tags, and if there is a words like: مدينه dont add it",
        },
    ]

    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    keywords = response.choices[0].message["content"].strip()
    return keywords


import re


def generate_response(feeds_titles, feeds_descriptions, feeds_urls, question):
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

    context_str = ""
    for i, feed in enumerate(list(zip(feeds_titles, feeds_descriptions, feeds_urls))):
        context_str += f"""
            <source_id> {i+1} </source_id>
            <title> {feed[0]} </title>
            <description> {feed[1]} </description>
            <url> {feed[2]} </url>
            
         """

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Write an answer to the following question.",
        },
        {
            "role": "user",
            "content": f"""
        ### Task:
        Respond to the user query using the provided context, incorporating inline citations in the format [source_id] **only when the <source_id> tag is explicitly provided** in the context.

        ### Guidelines:
        - If you don't know the answer, clearly state that.
        - If uncertain, ask the user for clarification.
        - Respond in the same language as the user's query.
        - If the context is unreadable or of poor quality, inform the user and provide the best possible answer.
        - If the answer isn't present in the context but you possess the knowledge, explain this to the user and provide the answer using your own understanding.
        - **Only include inline citations using [source_id] when a <source_id> tag is explicitly provided in the context.**  
        - Do not cite if the <source_id> tag is not provided in the context.  
        - Do not use XML tags in your response.
        - Ensure citations are concise and directly related to the information provided.

        ### Example of Citation:
        If the user asks about a specific topic and the information is found in "whitepaper.pdf" with a provided <source_id>, the response should include the citation like so:  
        * "According to the study, the proposed method increases efficiency by 20% [whitepaper.pdf]."
        If no <source_id> is present, the response should omit the citation.

        ### Output:
        Provide a clear and direct response to the user's query, including inline citations in the format [source_id] only when the <source_id> tag is present in the context.

        <context>
        {context_str}
        </context>

        <user_query>
        {question}
        </user_query>
        """,
        },
    ]

    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    answer = response.choices[0].message["content"].strip()
    cleaned_response = answer.replace("\n", " ").strip()
    numbers = re.findall(r"\[(\d+)\]", cleaned_response)
    numbers = [int(num) for num in numbers]

    if len(numbers) == 0:
        return cleaned_response
    cleaned_response += """

    references:

    """
    for i, n in enumerate(numbers):
        cleaned_response.replace(f"[{n}]", f"[{i+1}]")
        cleaned_response += f"[{i+1}] {feeds_urls[n-1]} \n"
    return cleaned_response

def ask_question_v2(data: dict, request):
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
    question: str = data["question"]
    date_range_start: str = data.get("date_range_start")
    date_range_end: str = data.get("date_range_end")
    user_id = request.user.id
    feeds = get_best_matched_feeds(question,user_id, date_range_start, date_range_end)
    if not feeds:
        return {
            "success": False,
            "message": "Be more specific, your question is not related to any feed or no feeds found in this date range",
            "payload": "Be more specific, your question is not related to any feed or no feeds found in this date range",
        }

    # Send this feeds as a context to GPT
    feeds_titles = list(feeds.values_list("title", flat=True))
    feeds_descriptions = list(feeds.values_list("description", flat=True))
    feeds_urls = list(feeds.values_list("url", flat=True))
    print(feeds_titles)

    # Generate response from GPT
    response = generate_response(feeds_titles, feeds_descriptions, feeds_urls, question)

    # Save the response to the database
    UserQuery.objects.create(
        user=request.user,
        question=question,
        answer=response,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
    )
    
    return {
        "success": True,
        "message": "Feeds fetched successfully",
        "payload": response,
    }
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
    question: str = data["question"]
    date_range_start: str = data.get("date_range_start")
    date_range_end: str = data.get("date_range_end")

    tags: json = extrat_tags_from_question(question)
    tags_dict: dict = json.loads(tags)
    print(tags_dict)
    categories: list = list(tags_dict.keys())
    original_tags = [tag for tags in tags_dict.values() for tag in tags]
    similar_tags = get_similar_tags(original_tags)
    print("similar tags: ", similar_tags)
    similar_tags = [str(tag) for tag in similar_tags]
    tags = Tag.objects.filter(name__in=similar_tags).distinct()
    print(tags.values())

    feeds_filters = {"tags__in": tags}
    if date_range_start:
        feeds_filters["created_at__date__gte"] = date_range_start
    if date_range_end:
        feeds_filters["created_at__date__lte"] = date_range_end
    if date_range_start and date_range_end:
        feeds_filters["created_at__date__range"] = (date_range_start, date_range_end)

    feeds = Feed.objects.filter(**feeds_filters).distinct()

    if not feeds:
        return {
            "success": False,
            "message": "Be more specific, your question is not related to any feed or no feeds found in this date range",
            "payload": "Be more specific, your question is not related to any feed or no feeds found in this date range",
        }

    # Send this feeds as a context to GPT
    feeds_titles = list(feeds.values_list("title", flat=True))
    feeds_descriptions = list(feeds.values_list("description", flat=True))
    feeds_urls = list(feeds.values_list("url", flat=True))
    print(feeds_titles)

    # Generate response from GPT
    response = generate_response(feeds_titles, feeds_descriptions, feeds_urls, question)

    # Save the response to the database
    UserQuery.objects.create(
        user=request.user,
        question=question,
        answer=response,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        tags=tags_dict,
    )

    return {
        "success": True,
        "message": "Feeds fetched successfully",
        "payload": response,
    }
