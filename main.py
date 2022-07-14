from News.g1_news import G1News

if __name__ == '__main__':
    g1 = G1News()

    parsed_news = g1.retrieve_news(max_pages=1, region_lock=False, regions=[
        'am', 'ac', 'pa', 'rr', 'ro', 'ap', 'to'
    ])
    g1.export_data(parsed_data=g1.parse_news(parsed_news), export_type='json')
