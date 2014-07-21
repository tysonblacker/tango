import json
import urllib, urllib2
import sys

def run_query_global(search_terms):
    # Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    """
    https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%27web%27&Query=%27raspberry%20pi%27&Options=%27EnableHighlighting%27 
    """
    source = 'Web'
    
    results_per_page = 10
    offset = 3
 
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    search_url = "{0}{1}?Query={4}&$top={2}&$skip={3}&$format=json".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)

    #print search_url

    #search_url = "https://api.datamarket.azure.com/Bing/Search/Web?Query=%27raspberry%20pi%27&$top=2&$format=json"
    print search_url

    username = ''
    bing_api_key = "ITXDkhGtSjyrW6+TPJCV284egtJ2RtCBoFtyqyBKKrk"

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, bing_api_key)

    results = []

    try:
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        response = urllib2.urlopen(search_url).read()

        #print response
        #print "---------------------------------"
        json_response = json.loads(response)

        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})


    except urllib2.URLError, e:
        print "Error when trying to query the Bing API ", e

    return results

    

def main(argv=None):
 
    print "What's ya query"
    q = sys.stdin.readline()
    """
    if len(argv) > 1:
        q = argv[1]
    else:
        q = "raspberry"
    """
    print run_query_global(q)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
