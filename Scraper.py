from lxml import html
import json
import requests
import re, urllib.parse
import pandas as pd
import os
import glob


pageCount = 0
totalReviewCount = 0
getNewData = False
baseDir = "C:/Users/mkhullar/PycharmProjects/ScrapeYelp/"


def parse(url):
    global pageCount, totalReviewCount
    pageCount += 1
    yelp_id = url.split('/')[-1]
    response = requests.get(url).text
    parser = html.fromstring(response)
    print("Parsing the page: " + str(pageCount))
    raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")
    raw_claimed = parser.xpath("//span[contains(@class,'claim-status_icon--claimed')]/parent::div/text()")
    raw_review_count = parser.xpath(
        "//div[contains(@class,'biz-main-info')]//span[contains(@class,'review-count rating-qualifier')]//text()")
    raw_category = parser.xpath('//div[contains(@class,"biz-page-header")]//span[@class="category-str-list"]//a/text()')
    hours_table = parser.xpath("//table[contains(@class,'hours-table')]//tr")
    details_table = parser.xpath("//div[@class='short-def-list']//dl")
    raw_map_link = parser.xpath("//a[@class='biz-map-directions']/img/@src")
    raw_phone = parser.xpath(".//span[@class='biz-phone']//text()")
    raw_address = parser.xpath('//div[@class="mapbox-text"]//div[contains(@class,"map-box-address")]//text()')
    raw_wbsite_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
    raw_price_range = parser.xpath("//dd[contains(@class,'price-description')]//text()")
    raw_health_rating = parser.xpath("//dd[contains(@class,'health-score-description')]//text()")
    rating_histogram = parser.xpath("//table[contains(@class,'histogram')]//tr[contains(@class,'histogram_row')]")
    raw_ratings = parser.xpath("//div[contains(@class,'biz-page-header')]//div[contains(@class,'rating')]/@title")
    raw_related_business = parser.xpath('//div[contains(@class,\'related-businesses\')]//li')
    working_hours = []
    for hours in hours_table:
        raw_day = hours.xpath(".//th//text()")
        raw_timing = hours.xpath("./td//text()")
        day = ''.join(raw_day).strip()
        timing = ''.join(raw_timing).strip().split('\n')[0]
        working_hours.append({day: timing})
    info = []
    for details in details_table:
        raw_description_key = details.xpath('.//dt//text()')
        raw_description_value = details.xpath('.//dd//text()')
        description_key = ''.join(raw_description_key).strip()
        description_value = ''.join(raw_description_value).strip()
        info.append({description_key: description_value})

    ratings_histogram = []
    for ratings in rating_histogram:
        raw_rating_key = ratings.xpath(".//th//text()")
        raw_rating_value = ratings.xpath(".//td[@class='histogram_count']//text()")
        rating_key = ''.join(raw_rating_key).strip()
        rating_value = ''.join(raw_rating_value).strip()
        ratings_histogram.append({rating_key: rating_value})

    relatedBusiness = list()
    for business in raw_related_business:
        tempBusiness = dict()
        name = business.xpath('.//div/div[contains(@class,\'media-story\')]/div[contains(@class,\'media-title\')]'
                              '/a/span')[0].text
        href = business.xpath('.//div/div[contains(@class,\'media-story\')]/div[contains(@class,\'media-title\')]'
                              '/a/@href')[0].split('?')[0]
        b_rating = business.xpath('.//div/div[contains(@class,\'media-story\')]/div[contains(@class,\'biz-rating\')]'
                                  '/div/@title')[0].split('.')[0]
        b_review = business.xpath('.//div/div[contains(@class,\'media-story\')]/div[contains(@class,\'biz-rating\')]'
                                  '/span')[0].text
        b_info = business.xpath('.//div/div[contains(@class,\'media-story\')]/q')[0].text

        tempBusiness['yelp_id'] = href.strip().split('/')[2]
        tempBusiness['business_name'] = name.strip().encode('ascii',errors='ignore').decode('utf-8')
        tempBusiness['business_url'] = 'https://www.yelp.com'+href.strip()
        tempBusiness['business_rating'] = b_rating.strip()
        tempBusiness['business_reviews'] = b_review.strip()
        tempBusiness['business_info'] = b_info.strip().encode('ascii',errors='ignore').decode('utf-8')
        relatedBusiness.append(tempBusiness)

    name = ''.join(raw_name).strip()
    phone = ''.join(raw_phone).strip()
    address = ' '.join(' '.join(raw_address).split())
    health_rating = ''.join(raw_health_rating).strip()
    price_range = ''.join(raw_price_range).strip()
    claimed_status = ''.join(raw_claimed).strip()
    reviewCount = ''.join(raw_review_count).strip()
    category = ','.join(raw_category)
    cleaned_ratings = ''.join(raw_ratings).strip()

    if raw_wbsite_link:
        decoded_raw_website_link = urllib.parse.unquote(raw_wbsite_link[0])
        website = re.findall("biz_redir\?url=(.*)&website_link", decoded_raw_website_link)[0]
    else:
        website = ''

    if raw_map_link:
        decoded_map_url = urllib.parse.unquote(raw_map_link[0])
        map_coordinates = ['','']
        if len(re.findall("center=([+-]?\d+.\d+,[+-]?\d+\.\d+)", decoded_map_url)) > 0:
            map_coordinates = re.findall("center=([+-]?\d+.\d+,[+-]?\d+\.\d+)", decoded_map_url)[0].split(',')
        elif decoded_map_url.__contains__('png|'):
            map_coordinates = decoded_map_url.split('png|')[1].split('&')[0].split(',')
        latitude = map_coordinates[0]
        longitude = map_coordinates[1]
    else:
        latitude = ''
        longitude = ''

    if raw_ratings:
        ratings = re.findall("\d+[.,]?\d+", cleaned_ratings)[0]
    else:
        ratings = 0

    reviews = dict()
    reviewList = list()
    reviews['count'] = reviewCount
    if reviewCount is not '':
        tempCount = int(reviewCount.split(' ')[0].strip())
        totalReviewCount += tempCount
        for j in range(0,tempCount, 20):
            tempUrl = url + '?start=' + str(j)
            response = requests.get(tempUrl).text
            parser = html.fromstring(response)
            raw_reviews = parser.xpath("//div[@class='review-list']/ul/li")
            for i in range(1, len(raw_reviews)):
                tempList = list()
                tempUser = list()
                tempReview = list()
                raw_full_user_data = raw_reviews[i].xpath('.//div/div[contains(@class,\'review-sidebar\')]/div/div/'
                                                          'div[contains(@class,\'media-story\')]')
                raw_profile_pic = raw_reviews[i].xpath('.//div/div[contains(@class,\'review-sidebar\')]/div/div/'
                                                       'div[contains(@class,\'media-avatar\')]')
                if len(raw_full_user_data)>0:
                    raw_user_data = raw_full_user_data[0].xpath('.//ul[contains(@class,\'user-passport-info\')]')
                    raw_user_name = raw_user_data[0].xpath('.//li[contains(@class, \'user-name\')]/a/text()')[0] \
                        if len(raw_user_data[0].xpath('.//li[contains(@class, \'user-name\')]/a/text()'))>0 else ""
                    raw_user_id = raw_user_data[0].xpath('.//li[contains(@class, \'user-name\')]/a/@href')[0] \
                        if len(raw_user_data[0].xpath('.//li[contains(@class, \'user-name\')]/a/@href'))>0 else ""
                    user_id = raw_user_id.split('userid=')[1] if raw_user_id != "" else ""
                    tempUser.append({'User_id': user_id.strip()})
                    tempUser.append({'User_Name': raw_user_name.strip()})
                    raw_user_city = raw_user_data[0].xpath('.//li[contains(@class, \'user-location\')]/b/text()')[0] \
                        if len(raw_user_data[0].xpath('.//li[contains(@class, \'user-location\')]/b/text()')) > 0 else ''
                    tempUser.append({'City': raw_user_city.strip()})

                    raw_user_other = raw_full_user_data[0].xpath('.//ul[contains(@class,\'user-passport-stats\')]')
                    raw_user_friend_count = raw_user_other[0].xpath('.//li[contains(@class,\'friend-count\')]/b/text()')[0]
                    tempUser.append({'Friend': int(raw_user_friend_count.strip())})
                    reviewPP = False
                    if raw_user_name !='':
                        reviewPP = False \
                        if 'img/default_avatars' in str(raw_profile_pic[0].xpath('.//div/a/img/@src')[0]) \
                        else True
                    review_PP_Url = ''
                    if reviewPP:
                        review_PP_Url = str(raw_profile_pic[0].xpath('.//div/a/img/@src')[0])
                    tempUser.append({'Profile_Pic': reviewPP})
                    tempUser.append({'Profile_Pic_Url': review_PP_Url.strip()})
                    raw_user_review_count = raw_user_other[0].xpath('.//li[contains(@class,\'review-count\')]/b/text()')[0]
                    tempUser.append({'Reviews': int(raw_user_review_count.strip())})
                    tempList.append({'User': tempUser})
                    raw_review_id = raw_reviews[i].xpath('.//div/@data-review-id')[0]
                    raw_review = ''
                    for raw_rev in raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]/'
                                                        'div[contains(@class,\'review-content\')]/p/text()'):
                        raw_review += raw_rev
                    raw_review_date = raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]/'
                                                    'div[contains(@class,\'review-content\')]/div/span')[0].text
                    raw_review_rating = raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]/'
                                                    'div[contains(@class,\'review-content\')]/div/div/div/@title')[0]
                    raw_review_image = True \
                        if len(raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]'
                                                    '/div[contains(@class,\'review-content\')]/'
                                                    'ul[contains(@class,\'photo-box-grid\')]')) > 0 \
                        else False
                    raw_review_image_url = ''
                    if raw_review_image:
                        raw_review_image_url = raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]'
                                                    '/div[contains(@class,\'review-content\')]/ul/li/div/img/@data-async-src')[0]
                    raw_review_useful_list = raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]/'
                                                                  'div[contains(@class,\'review-footer\')]/div/ul/li')
                    usedict = dict()
                    for raw_review_useful in raw_review_useful_list:
                        vote_type = raw_review_useful.xpath('./a/span[contains(@class,\'vote-type\')]')[0].text
                        count = raw_review_useful.xpath('./a/span[contains(@class,\'count\')]')[0].text
                        usedict[vote_type.strip()] = int(count.strip()) if count is not None else 0

                    tempReview.append({'review_id': raw_review_id.strip()})
                    tempReview.append({'date': raw_review_date.strip()})
                    tempReview.append({'rating': raw_review_rating.strip()})
                    tempReview.append({'review_pic': raw_review_image})
                    tempReview.append({'review_pic_url': raw_review_image_url.split(' ')[0]})
                    tempReview.append({'reviewUse': usedict})
                    reviewVal = raw_review.strip().encode('ascii',errors='ignore')
                    tempReview.append({'review': reviewVal.decode("utf-8")})

                    tempList.append({'Review': tempReview})
                    # raw_review_rating = raw_reviews[i].xpath('./div/div[contains(@class,\'review-wrapper\')]/'
                    #                                          'div[contains(@class,\'clearfix\')]/p/text()')[0]
                    reviewList.append(tempList)
    reviews['info'] = reviewList

    data = {'yelp_id': yelp_id,
            'working_hours': working_hours,
            'info': info,
            'ratings_histogram': ratings_histogram,
            'name': name,
            'phone': phone,
            'ratings': ratings,
            'address': address,
            'health_rating': health_rating,
            'price_range': price_range,
            'claimed_status': claimed_status,
            'category': category,
            'website': website,
            'latitude': latitude,
            'longitude': longitude,
            'url': url,
            'related_business': relatedBusiness,
            'reviews': reviews
            }
    return data


def getJsonData(fileName, urls):
    for idx, url in enumerate(urls):
        try:
            scraped_data = parse(url)
            with open(baseDir+"Json/"+"scraped_data-%s.json" % fileName, 'a') as fp:
                json_text = json.dumps(scraped_data)
                fp.write("{}\n".format(json_text))
        except:
            print("getJsonData Error" + url)
            time.sleep(60)
            scraped_data = parse(url)
            with open(baseDir + "Json/" + "scraped_data-%s.json" % fileName, 'a') as fp:
                json_text = json.dumps(scraped_data)
                fp.write("{}\n".format(json_text))
            continue


def getAllURL(url):
    listLinks = list()
    temp_response = requests.get(url + '&start=0').text
    temp_parser = html.fromstring(temp_response)
    temp_raw_List = temp_parser.xpath('//ul[contains(@class,\'search-results\')][2]/'
                                      'li[contains(@class,\'regular-search-result\')]')

    listLength = len(temp_raw_List)

    for i in range(0, 1000, listLength):
        try:
            response = requests.get(url+'&start='+str(i)).text
            parser = html.fromstring(response)
            raw_List = parser.xpath('//ul[contains(@class,\'search-results\')][2]/'
                                    'li[contains(@class,\'regular-search-result\')]')

            for link in raw_List:
                listLinks.append('https://www.yelp.com'
                                 + link.xpath('.//div/div[contains(@class,\'biz-listing-large\')]'
                                              '/div[contains(@class,\'main-attributes\')]/div/div[contains(@class,'
                                              '\'media-story\')]/h3/span/a/@href')[0].split('?')[0])
            if len(raw_List) < listLength:
                break
        except:
            print("error in getAllURL")
            time.sleep(60)
            response = requests.get(url + '&start=' + str(i)).text
            parser = html.fromstring(response)
            raw_List = parser.xpath('//ul[contains(@class,\'search-results\')][2]/'
                                    'li[contains(@class,\'regular-search-result\')]')

            for link in raw_List:
                listLinks.append('https://www.yelp.com'
                                 + link.xpath('.//div/div[contains(@class,\'biz-listing-large\')]'
                                              '/div[contains(@class,\'main-attributes\')]/div/div[contains(@class,'
                                              '\'media-story\')]/h3/span/a/@href')[0].split('?')[0])
            if len(raw_List) < listLength:
                break
            continue
    tempSet = set(listLinks)
    tempList = list(tempSet)
    return tempList

# getJsonData('test', ['https://www.yelp.com/biz/professional-sitters-nc-raleigh-2'])


def createList(datas, city):
    reviewList = list()
    businessList = list()
    for data in datas:
        tempBusinessList= list()
        d = json.loads(data)
        yelp_id = d['yelp_id']
        for info in d['reviews']['info']:
            tempReviewList = list()
            tempReviewList.append(yelp_id)
            user = info[0]['User']
            Review = info[1]['Review']
            tempReviewList.append(Review[0]['review_id'])
            tempReviewList.append(city)
            tempReviewList.append(Review[1]['date'])
            tempReviewList.append(user[0]['User_id'])
            tempReviewList.append(user[1]['User_Name'])
            tempReviewList.append(user[2]['City'])
            tempReviewList.append(user[3]['Friend'])
            tempReviewList.append(user[4]['Profile_Pic'])
            tempReviewList.append(user[5]['Profile_Pic_Url'])
            tempReviewList.append(user[6]['Reviews'])
            tempReviewList.append(Review[2]['rating'].split('.')[0])
            tempReviewList.append(Review[3]['review_pic'])
            tempReviewList.append(Review[4]['review_pic_url'])
            if Review[5]['reviewUse']:
                tempReviewList.append(Review[5]['reviewUse']['Useful'])
                tempReviewList.append(Review[5]['reviewUse']['Funny'])
                tempReviewList.append(Review[5]['reviewUse']['Cool'])
            else:
                tempReviewList.extend([0,0,0])
            tempReviewList.append(Review[6]['review'])
            reviewList.append(tempReviewList)
        tempBusinessList.append(yelp_id)
        tempBusinessList.append(d['name'])
        tempBusinessList.append(d['phone'])
        tempBusinessList.append(d['address'])
        tempBusinessList.append(d['ratings'])
        tempBusinessList.append(d['health_rating'])
        tempBusinessList.append(d['price_range'])
        tempBusinessList.append(d['claimed_status'])
        tempBusinessList.append(d['category'])
        tempBusinessList.append(d['website'])
        tempBusinessList.append(d['latitude'])
        tempBusinessList.append(d['longitude'])
        tempBusinessList.append(d['url'])
        if len(d['ratings_histogram']) > 0:
            tempBusinessList.append(d['ratings_histogram'][0]['5 stars'])
            tempBusinessList.append(d['ratings_histogram'][1]['4 stars'])
            tempBusinessList.append(d['ratings_histogram'][2]['3 stars'])
            tempBusinessList.append(d['ratings_histogram'][3]['2 stars'])
            tempBusinessList.append(d['ratings_histogram'][4]['1 star'])
        businessList.append(tempBusinessList)
    return reviewList, businessList


def jsonToCSV(file):
    f = open(baseDir+'convert_json_new/'+file)
    data = json.loads(json.dumps(list(f)))
    reviewList, businessList = createList(data, file.split('.json')[0].split('-')[1].replace('_', ''))
    if reviewList:
        df = pd.DataFrame(reviewList)
        df.columns = ['yelp_id', 'review_id', 'GeneralCity', 'review_date', 'user_id', 'user_name', 'City', 'friend_count',
                      'Profile_pic', 'profile_pic_url', 'review_count', 'rating', 'review_pic', 'review_pic_url',
                      'Useful', 'Funny', 'Cool', 'review']
        df.to_csv(baseDir+'CSV/'+'review_'+file.replace(' ', '_').replace('-', '_')+'.csv', index=False)
    if businessList:
        df1 = pd.DataFrame(businessList)
        df1.columns = ['yelp_id', 'business_name', 'phone_no', 'address', 'ratings',
                       'health_rating', 'price_range', 'claimed_status', 'category', 'website',
                       'latitude', 'longitude', 'yelp_url', '5 stars', '3 stars', '4 stars',
                       '2 stars', '1 star']
        df1.to_csv(baseDir+'CSV/'+'business_'+file.replace(' ', '_').replace('-', '_')+'.csv', index=False)





if __name__ == "__main__":
    searchTerm = 'Child Care %26 Day Care'
    # cities1 = ['Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego',
    #           'Dallas', 'San Jose']
    # cities2 = ['Austin', 'Jacksonville', 'San Francisco', 'Columbus', 'Indianapolis', 'Fort Worth', 'Charlotte',
    #            'Seattle', 'Denver', 'El Paso']
    Done = ['Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose','Boston','Detroit','Nashville',
            'Memphis', 'Portland', 'Oklahoma City','Las Vegas', 'Louisville', 'Baltimore', 'Milwaukee', 'Albuquerque',
            'Tucson', 'Fresno', 'Sacramento','Mesa', 'Kansas City', 'Atlanta', 'Long Beach', 'Colorado Springs']

    # citiesList = [['Oakland', 'Minneapolis', 'Tulsa', 'Arlington', 'New Orleans', 'Wichita']]
    # citiesList = [['Cleveland', 'Tampa', 'Bakersfield', 'Aurora', '	Honolulu', 'Anaheim', 'Santa Ana', 'Corpus Christi',
                  # 'Riverside', 'Lexington', 'St. Louis', 'Stockton', 'Pittsburgh', 'Saint Paul', 'Cincinnati',
                  # 'Anchorage', 'Henderson', 'Greensboro', 'Plano', 'Newark', 'Lincoln', 'Toledo', 'Orlando',
                  # 'Chula Vista', 'Irvine', 'Fort Wayne']]
    # citiesList = ['Oakland', 'Minneapolis', 'Tulsa', 'Arlington', 'New Orleans', 'Wichita', 'Jersey City', 'Durham',
    #               'St. Petersburg', 'Laredo', 'Buffalo', 'Madison', 'Lubbock', 'Chandler', 'Scottsdale', 'Glendale',
    #               'Reno', 'Norfolk', 'Winston–Salem', 'North Las Vegas''Cleveland', 'Tampa', 'Bakersfield', 'Aurora',
    #               '	Honolulu', 'Anaheim', 'Santa Ana', 'Corpus Christi', 'Riverside', 'Lexington', 'St. Louis',
    #               'Stockton', 'Pittsburgh', 'Saint Paul', 'Cincinnati','Anchorage', 'Henderson', 'Greensboro', 'Plano',
    #               'Newark', 'Lincoln', 'Toledo', 'Orlando', 'Chula Vista', 'Irvine', 'Fort Wayne']
    citiesList = [['Irving', 'Chesapeake', 'Gilbert', 'Hialeah', 'Garland', 'Fremont', 'Baton Rouge', 'Richmond',
                  'Boise', 'San Bernardino']]
    if getNewData:
        import time
        for cities in citiesList:
            try:
                for city in cities:
                    try:
                        urlLink = dict()
                        urlLink[city] = getAllURL('https://www.yelp.com/search?find_desc=' + searchTerm.replace(' ', '+') +
                                                  '&find_loc=' + city.replace(' ', '+'))
                    except:
                        print("Stuck in getting data for business")
                        time.sleep(60)
                        continue
                    summaryDict = dict()
                    for key, value in urlLink.items():
                        try:
                            getJsonData(key, value)
                        except:
                            print("Some errors in getJsonData for loop")
                            time.sleep(60)
                            continue
                        print(key+': ', totalReviewCount)
                        summaryDict[key] = int(totalReviewCount)
                        print(summaryDict)
            except:
                print("Some errors in citiesList for loop")
                time.sleep(60)
                continue
    os.chdir(baseDir+'convert_json_new/')
    files = glob.glob('*.json')
    for file in files:
        print(file)
        jsonToCSV(file)
    pass