from yelpapi import YelpAPI


def check_closed():
    yelp_api = YelpAPI('-yAXhyllgHQXEdjcrjbG1FauDw8pOIeymK0e0dIW8uVZFRrDGs4jSF5txgBMKwW2Ji3MqghZq04HwKuhtqPJTWM2MwQbhzIDa1_DDM-7qCKfUm0t33lk7D0F2UzWWnYx')
    business = yelp_api.search_query(term='Ladybug and Friends Daycare and Preschool', location='chicago, IL',
                                     yelp_business_id='ladybug-and-friends-daycare-and-preschool-chicago-3', limit=1)
    search_results = yelp_api.business_query(business['businesses'][0]['id'])
    print(search_results['is_closed'])
    pass

check_closed()