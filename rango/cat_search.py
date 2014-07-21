import json
import urllib, urllib2
import sys
from rango.models import Page

def run_query(search_terms):
    list = Page.objects.filter(title__contains=search_terms)
    print list
    return list

def run_query_cat(cat, page_filter):
    list = Page.objects.filter(category=cat)
    list = list.filter(title__contains=page_filter)
    print list
    return list

    

def main(argv=None):
 
    print "What's ya query"
    q = sys.stdin.readline()
    """
    if len(argv) > 1:
        q = argv[1]
    else:
        q = "raspberry"
    """
    print run_query(q)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
