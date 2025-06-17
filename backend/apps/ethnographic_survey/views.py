# ethnograghic_survey/views.py
from django.shortcuts import render, redirect
from .forms import EthnographicSurveyForm
from .models import EthnographicSurvey
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.db.models.functions import TruncDate, Lower, Trim
import json
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import plotly.express as px
from .utils.nlp_tools import summarize_text
from .utils.text_preprocessing import preprocess_text, extract_tfidf_keywords, perform_topic_modeling
from .utils.visualization import generate_wordcloud_image, generate_tfidf_plot


def survey_form(request):
    if request.method == 'POST':
        form = EthnographicSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thank_you')
    else:
        form = EthnographicSurveyForm()
    return render(request, 'ethnographic_survey/survey_form.html', {'form': form})

def thank_you(request):
    return render(request, 'ethnographic_survey/thank_you.html')

@staff_member_required
def dashboard(request):
    query = request.GET.get('q')
    surveys = EthnographicSurvey.objects.all().order_by('-date_submitted')
    if query:
        surveys = surveys.filter(
            Q(name__icontains=query) |
            Q(gender__icontains=query) |
            Q(village__icontains=query) |
            Q(occupation__icontains=query) |
            Q(language_spoken__icontains=query)
        )

    paginator = Paginator(surveys, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

     # Aggregated data for charts
    gender_data = list(
        surveys
        .annotate(clean_gender=Trim(Lower('gender')))
        .values('clean_gender')
        .annotate(count=Count('clean_gender'))
        .order_by('-count')
    )

    gender_data = [
        {'label': (entry['clean_gender'] or 'Unknown').title(), 'count': entry['count']}
        for entry in gender_data
    ]

    village_data = list(
        surveys
        .annotate(clean_village=Trim(Lower('village')))
        .values('clean_village')
        .annotate(count=Count('clean_village'))
        .order_by('-count')
    )

    village_data = [
        {'label': (entry['clean_village'] or 'Unknown').title(), 'count': entry['count']}
        for entry in village_data
    ]

    language_data = list(
        surveys
        .annotate(clean_lang=Trim(Lower('language_spoken')))
        .values('clean_lang')
        .annotate(count=Count('clean_lang'))
        .order_by('-count')
    )

    language_data = [
        {'label': (entry['clean_lang'] or 'Unknown').title(), 'count': entry['count']}
        for entry in language_data
    ]

    submission_data = list(
    surveys.annotate(date=TruncDate('date_submitted'))
           .values('date')
           .annotate(count=Count('id'))
           .order_by('date')
)
    submission_data = [
    {'label': entry['date'].strftime('%Y-%m-%d'), 'count': entry['count']}
    for entry in submission_data
]

    return render(request, 'ethnographic_survey/dashboard.html', {
        'surveys': page_obj,
        'query': query,
        'gender_data': json.dumps(gender_data),
        'village_data': json.dumps(village_data),
        'language_data': json.dumps(language_data),
        'submission_data': json.dumps(submission_data),
    })

@staff_member_required
def export_surveys(request, file_format):
    surveys = EthnographicSurvey.objects.all().values()
    df = pd.DataFrame(surveys)

    # Convert datetime fields to timezone-unaware
    for col in df.select_dtypes(include=['datetimetz']).columns:
        df[col] = df[col].dt.tz_localize(None)

    if file_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=surveys.csv'
        df.to_csv(path_or_buf=response, index=False)
        return response

    elif file_format == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=surveys.xlsx'
        df.to_excel(response, index=False, engine='openpyxl')
        return response

    elif file_format == 'parquet':
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=surveys.parquet'
        df.to_parquet(response, index=False, engine='pyarrow')
        return response

    return HttpResponse("Unsupported format", status=400)

def correlation_heatmap(request):
    # Step 1: Extract relevant fields
    df = pd.DataFrame.from_records(
        EthnographicSurvey.objects.values(
            'gender', 'village', 'local_origin', 'cultural_practice'
        )
    )
    df.fillna('Unknown', inplace=True)

    if df.empty:
        return render(request, 'ethnographic_survey/correlation.html', {
            'plot_div': "<p>No data available to generate heatmap.</p>"
        })

    # Step 2: One-hot encode
    encoder = OneHotEncoder(sparse_output=False)
    encoded_array = encoder.fit_transform(df)
    encoded_df = pd.DataFrame(encoded_array, columns=encoder.get_feature_names_out())

    # Step 3: Correlation matrix (filtering target vs. source fields)
    correlation_matrix = encoded_df.corr().loc[
        encoded_df.columns.str.startswith(('gender_', 'village_', 'local_origin_')),
        encoded_df.columns.str.startswith('cultural_practice_')
    ]

    # Step 4: Plotly heatmap
    fig = px.imshow(
        correlation_matrix,
        aspect="auto",
        color_continuous_scale='RdBu',
        title="Correlation Heatmap: Gender, Village, LGA vs Cultural Practices",
        labels=dict(x="Cultural Practices", y="Demographic Factors")
    )
    fig.update_layout(margin=dict(l=40, r=40, t=60, b=40))
    plot_div = fig.to_html(full_html=False)

    # Step 5: Render
    return render(request, 'ethnographic_survey/correlation.html', {
        'plot_div': plot_div
    })

def wordcloud_and_tfidf(request):
    texts = EthnographicSurvey.objects.values_list('oral_history', flat=True)
    full_text = ' '.join(filter(None, texts))
    wordcloud_img, wordcloud_base64 = generate_wordcloud_image(full_text)
    tfidf_keywords = extract_tfidf_keywords(full_text, top_n=20)
    tfidf_plot_html = generate_tfidf_plot(tfidf_keywords)
    return render(request, 'ethnographic_survey/wordcloud_tfidf.html', {
        'wordcloud_base64': wordcloud_base64,
        'tfidf_plot_html': tfidf_plot_html,
    })

def summary_view(request):
    entries = EthnographicSurvey.objects.exclude(oral_history__isnull=True).exclude(oral_history__exact='')
    summarized = [
        {
            "name": entry.name,
            "original": entry.oral_history,
            "summary": summarize_text(entry.oral_history)
        }
        for entry in entries
    ]
    return render(request, "ethnographic_survey/summary_view.html", {"summaries": summarized})

def topic_modeling_view(request):
    texts = EthnographicSurvey.objects.values_list('oral_history', flat=True)
    documents = [text for text in texts if text]
    parsed_topics = perform_topic_modeling(documents)
    return render(request, 'ethnographic_survey/topic_modeling.html', {
        'topics': parsed_topics
    })

