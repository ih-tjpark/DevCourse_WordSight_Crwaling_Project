from datetime import datetime
import json
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from new_api.models import News, Keyword, Tag
from new_api.views import NewsList
from new_api.keyword_analysis import get_relation_keyword
from django.template.loader import render_to_string
from new_api.filters import NewsFilter
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from new_api.paginators import CustomPagination


def index(request):
    news_list = NewsList.as_view()(request).data['results']
    page_obj = NewsList.as_view()(request).data['page_obj']
    trend_keyword = Keyword.objects.all().order_by('-count')[:10]
    context = {'news_list': news_list, 'page_obj': page_obj, 'trend_keyword': trend_keyword }
    return render(request, "base.html", context)

def detail(request, news_id):
    news = get_object_or_404(News, news_id=news_id)
    tag = news.tag.all()
    trend_keyword = Keyword.objects.all().order_by('-count')[:10]
    context = {'news': news, 'tag': tag, 'trend_keyword': trend_keyword}
    return render(request, "pages/detail.html", context)

def updateNews(request, tag=None, agency=None):
    params = dict().fromkeys(['tags', 'agencys'])
    if request.method == 'POST':
        data = json.loads(request.body)
        tags = data.get('tags', [])
        agencys = data.get('agencys', [])
        params={'tags': ",".join(tags), 'agencys': ",".join(agencys)}
        test = NewsFilter(params['tags'], params['agencys'])
        news_obj = test.get_news()
        # print(news_obj)
        paginator = Paginator(news_obj, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        rendered = render_to_string("partial/newsDisplay.html", {"news_list": news_obj, "page_obj": page_obj})
        return HttpResponse(rendered)
    else:
        return HttpResponseBadRequest()

def error404view(request, exception=None):
    return render(request, 'pages/404page.html')

def search(request):
    if request.method == "GET":
        search_key = request.GET.get('q')
        if search_key:
            try:
                keyword = Keyword.objects.get(name=search_key)
                relation_keyword = get_relation_keyword(search_key)
                news = keyword.news_set.all()[:5]
                trend_keyword = Keyword.objects.all().order_by('-count')[:10]
                related_tag= Tag.objects.none()
                for n in news:
                    related_tag = related_tag | n.tag.all()

                date_graph = dict()
                for word in list(keyword.in_date.strip("[]").split(", ")):
                    word = word.strip("\"")
                    date_graph[word] = date_graph.get(word, 0) + 1
                date_graph = sorted(date_graph.items(), key=lambda x: x[0])
                date_graph = [(datetime.strptime(x[0],'%Y-%m-%d').strftime("%m월 %d일").lstrip("0").replace(" 0", " "),
                                x[1]*100//int(keyword.count)) for x in date_graph]
                context= {"keyword": keyword, 
                        "relation_keyword":relation_keyword,
                        "news":news, 
                        'trend_keyword':trend_keyword, 
                        "related_tag":related_tag[:5],
                        "date_graph":date_graph 
                }
                if relation_keyword:
                    return render(request, "pages/insight.html", context)
            except ObjectDoesNotExist:
                return render(request, "pages/emptyWord.html")
        else:
            return render(request, "base.html")

def page(request):
    news_list = NewsList.as_view()(request).data['results']
    page_obj = NewsList.as_view()(request).data['page_obj']
    trend_keyword = Keyword.objects.all().order_by('-count')[:10]
    context = {'news_list': news_list, 'page_obj': page_obj, 'trend_keyword': trend_keyword }
    return render(request, "newsFilter.html", context)