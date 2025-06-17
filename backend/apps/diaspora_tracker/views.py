# diaspora_tracker/views.py
from django.db.models import Count, Q
from .models import DiasporaEntry
from .forms import DiasporaEntryForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
import pandas as pd
import io

def dashboard(request):
    query = request.GET.get('q', '')
    country_filter = request.GET.get('country', '')

    entries = DiasporaEntry.objects.all().order_by('-id')

    if query:
        entries = entries.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(profession__icontains=query)
        )

    if country_filter:
        entries = entries.filter(country__iexact=country_filter)

    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    country_data = (
        entries.values('country')
        .annotate(count=Count('country'))
        .order_by('-count')
    )

    year_data = (
        entries.values('year_migrated')
        .annotate(count=Count('year_migrated'))
        .order_by('year_migrated')
    )

    countries = DiasporaEntry.objects.values_list('country', flat=True).distinct()

    return render(request, 'diaspora_tracker/dashboard.html', {
        'page_obj': page_obj,
        'country_data': list(country_data),
        'year_data': list(year_data),
        'query': query,
        'country_filter': country_filter,
        'countries': countries,
    })

def submit_entry(request):
    if request.method == 'POST':
        form = DiasporaEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('diaspora_thank_you')
    else:
        form = DiasporaEntryForm()

    return render(request, 'diaspora_tracker/submit_entry.html', {'form': form})

def thank_you(request):
    return render(request, 'diaspora_tracker/thank_you.html')

def export_data(request, file_format):
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    queryset = DiasporaEntry.objects.all().values()
    df = pd.DataFrame(list(queryset))

    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)

    buffer = io.BytesIO()

    if file_format == "csv":
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="diaspora_data.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    elif file_format == "xlsx":
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename="diaspora_data.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return response

    elif file_format == "parquet":
        response = HttpResponse(content_type="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename="diaspora_data.parquet"'
        df.to_parquet(response, engine='pyarrow', index=False)
        return response

    else:
        return HttpResponse("Unsupported format", status=400)
