'''
slug: URL identifier


event-occurrence/
?slug=hungarian-grand-prix&
    order=-end_date&
    limit=3&
    fields=uid,slug,image_urls,image_urls__url,winner_3_url,winner_2_url,winner_1_url,race_season_url,race_season_url__year,nation_url,nation_url__iso_country_code,nation_url__name,nation_url__image_urls,nation_url__image_urls__url,name,official_name,winner_1_url__last_name,winner_2_url__last_name,winner_3_url__last_name,end_date,start_date,sessionoccurrence_urls,sessionoccurrence_urls__uid,sessionoccurrence_urls__slug,sessionoccurrence_urls__name,sessionoccurrence_urls__nbc_status,sessionoccurrence_urls__status,sessionoccurrence_urls__start_time,sessionoccurrence_urls__editorial_start_time,sessionoccurrence_urls__end_time,sessionoccurrence_urls__image_urls,sessionoccurrence_urls__image_urls__image_type,sessionoccurrence_urls__image_urls__url,sessionoccurrence_urls__content_urls,sessionoccurrence_urls__content_urls__uid,sessionoccurrence_urls__content_urls__title,sessionoccurrence_urls__content_urls__synopsis,sessionoccurrence_urls__content_urls__created,sessionoccurrence_urls__content_urls__slug,sessionoccurrence_urls__content_urls__image_urls,sessionoccurrence_urls__content_urls__image_urls__image_type,sessionoccurrence_urls__content_urls__image_urls__url,sessionoccurrence_urls__content_urls__vod_type_tag_urls,sessionoccurrence_urls__content_urls__vod_type_tag_urls__name,sessionoccurrence_urls__content_urls__items,sessionoccurrence_urls__content_urls__items__duration,circuit_url,circuit_url__name,circuit_url__short_name,circuit_url__image_urls,circuit_url__image_urls__url,sponsor_url,sponsor_url__colour,sponsor_url__image_urls,sponsor_url__image_urls__url&fields_to_expand=image_urls,circuit_url,circuit_url__image_urls,race_season_url,nation_url,nation_url__image_urls,winner_1_url,winner_2_url,winner_3_url,sessionoccurrence_urls,sessionoccurrence_urls__image_urls,sessionoccurrence_urls__content_urls,sessionoccurrence_urls__content_urls__items,sessionoccurrence_urls__content_urls__image_urls,sessionoccurrence_urls__content_urls__vod_type_tag_urls,sponsor_url,sponsor_url__image_urls
eventoccurrence_urls: List with events inluding their parameters:



Event parameters (prefix for request: event_occurence_urls__):
%%__API__%%/event-occurrence/?slug=%%__SLUG__%%&order=-end_date&fields=
    name: Name to display
    official_name: Official Name
    slug: URL representation
    start_date: Start Date of event
    end_date: End Date of event
    sponsor_url: URL of events main sponsor (prefix: sponsor_url__)
        colour: Colour of sponsor
        image_urls: Image urls of sponsor
            url: URL of image for sponsor
    image_urls: Image of URLs for event (prefix: image_urls__)
        url: URL of image
    uid: Session UID (internal?)
    race_season_url: URL object for race season (?)
        year: Year of race season
    nation_url: URL object for nation
        iso_country_code: ISO country code for nation
        name: Name of nation
        image_urls: Image URLs for nation
            url: URL of image
    winner_1_url: Winner 1 of Event
        last_name: Last name of winner 1
    winner_2_url: Winner 2 of Event
        last_name: Last name of winner 2
    winner_3_url: Winner 3 of Event
        last_name: Last name of winner 3


Session:
sessionoccurrence_urls: Main Object for Session
    status: Status of the session (replay, exceeded)
    editorial_start_time: Official start time
    name: Name of the session
    nbc_status: Same as status(?)
    start_time: Start Time of Session
    image_urls: Image URLs object for session:
        image_type: type of image
        url: URL of Session Image
    content_urls: Content objects for session (array)
        uid: Main Identifier for Content / Episode
        created: Date of creation
        items: Information about content
            duration: Duration of Content
        title: Title of content
        image_urls: Image URL for content
            image_type: type of image
            url: URL of Content Image
        synopsis: Information about content
        vod_type_tag_urls: Tags of Content
            name: name of tag
        slug: Slug of Content


curl 'https://f1tv.formula1.com/api/session-occurrence/?fields=uid,nbc_status,status,editorial_start_time,live_sources_path,data_source_id,global_channel_urls,global_channel_urls__uid,global_channel_urls__slug,global_channel_urls__self,channel_urls,channel_urls__ovps,channel_urls__slug,channel_urls__name,channel_urls__uid,channel_urls__self,channel_urls__driver_urls,channel_urls__driver_urls__driver_tla,channel_urls__driver_urls__driver_racingnumber,channel_urls__driver_urls__first_name,channel_urls__driver_urls__last_name,channel_urls__driver_urls__image_urls,channel_urls__driver_urls__image_urls__image_type,channel_urls__driver_urls__image_urls__url,channel_urls__driver_urls__team_url,channel_urls__driver_urls__team_url__name,channel_urls__driver_urls__team_url__colour,eventoccurrence_url,eventoccurrence_url__slug,eventoccurrence_url__circuit_url,eventoccurrence_url__circuit_url__short_name,session_type_url,session_type_url__name&fields_to_expand=global_channel_urls,channel_urls,channel_urls__driver_urls,channel_urls__driver_urls__image_urls,channel_urls__driver_urls__team_url,eventoccurrence_url,eventoccurrence_url__circuit_url,session_type_url&slug=2018-german-grand-prix-race' \
-XGET \
-H 'Host: f1tv.formula1.com' \
-H 'Accept: application/json, text/plain, */*' \
-H 'Connection: keep-alive' \
-H 'Accept-Language: DE, en' \
-H 'Accept-Encoding: br, gzip, deflate' \
-H 'Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6bnVsbCwiZXhwIjoxNTMzOTc0NDkyLCJpZCI6MTI0NDU2Mn0.6jDabIOWq_a28y6_Nt4WYDX4dTIGTeSD_nuv_ZIoyuU' \
-H 'Cookie: _ceg.s=pcmgae; _ceg.u=pcmgae; __zlcmid=mLhKVIhXW22Phx; re-html5-cc-options=%7B%22ccOn%22%3Afalse%2C%22font%22%3A%22Verdana%22%2C%22fontColor%22%3A%22%23FFF%22%2C%22fontSize%22%3A%22large%22%2C%22fontEdge%22%3A%22None%22%2C%22backgroundColor%22%3A%22%23000000%22%2C%22opacity%22%3A1%7D; _ga=GA1.2.280598681.1525961099; _gid=GA1.2.707988565.1532700344; userOriginCountry=DEU; player-audio-language=fx; subLang=en; jwtToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6bnVsbCwiZXhwIjoxNTMzOTc0NDkyLCJpZCI6MTI0NDU2Mn0.6jDabIOWq_a28y6_Nt4WYDX4dTIGTeSD_nuv_ZIoyuU; user-locale=DE; fw-uuid=b94178f9-f27e-40a8-8eb9-e006cd; __zlcprivacy=1' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15' \
-H 'If-Modified-Since: Sun, 29 Jul 2018 09:20:04 GMT' \
-H 'Referer: https://f1tv.formula1.com/DE/current-season/german-grand-prix/2018-german-grand-prix-race' \
-H 'X-CountryCode: zero'

%%__API__%%/session-occurence/?fields=status,channel_urls,channel_urls__ovps,channel_urls__slug,channel_urls__name&slug=2018-german-grand-prix-race

%%__API__%%/session-occurrence/?fields=
    uid,
    nbc_status,
    status,*
    editorial_start_time,
    live_sources_path,
    data_source_id,
    global_channel_urls,
        global_channel_urls__uid,
        global_channel_urls__slug,
        global_channel_urls__self,
    channel_urls,*
        channel_urls__ovps,*
        channel_urls__slug,*
        channel_urls__name,*
        channel_urls__uid,
        channel_urls__self,
        channel_urls__driver_urls,
            channel_urls__driver_urls__driver_tla,
            channel_urls__driver_urls__driver_racingnumber,
            channel_urls__driver_urls__first_name,
            channel_urls__driver_urls__last_name,
            channel_urls__driver_urls__image_urls,
            channel_urls__driver_urls__image_urls__image_type,
            channel_urls__driver_urls__image_urls__url,
            channel_urls__driver_urls__team_url,
            channel_urls__driver_urls__team_url__name,
            channel_urls__driver_urls__team_url__colour,
        eventoccurrence_url,
            eventoccurrence_url__slug,
            eventoccurrence_url__circuit_url,
            eventoccurrence_url__circuit_url__short_name,
        session_type_url,
            session_type_url__name
    &fields_to_expand=
        global_channel_urls,*
        channel_urls,
            channel_urls__driver_urls,
            channel_urls__driver_urls__image_urls,
            channel_urls__driver_urls__team_url,
        eventoccurrence_url,
            eventoccurrence_url__circuit_url,
            session_type_url
    &slug=2018-german-grand-prix-race

session_occurence:
    status: Status of session (replay, live, etc)
    session_url_type: Type of session_url
        name: Information about session (Race e.g.)
    editorial_start_time: Start time
    nbc_status: same as status (?)
    eventoccurrence_url: reference for event_occurence
        circuit_url: Information about Circuit
            short_name: Short name of Circuit
        slug: Slug for Event
    live_sources_path: ???
    channel_urls: Array of channels for this event
        uid: UID of channel
        self: complete API link
        driver_urls: If present - Information about driver in channel
            first_name: Drivers name
            last_name: Drivers last name
            image_urls: Images for driver
                image_type: Image type (helmet, etc.)
                url: URL of image
            driver_tla: Abbreviation for Driver
            team_url: Information about team of the driver
                colour: Colour of Team
                name: Name of Team
            driver_racingnumber: Number of Driver
        ovps: ???
            account_url: Information about account
            path: path for url
            domain: Domain to get Stream
            full_stream_url: URL of M3U8
        slug: Slug for Channel
        name: name of Channel


Episodes:

episodes/?slug=paddock-pass-post-race-in-hungary
    &fields=
        title,
        self,
        synopsis,
        image_urls,
        image_urls__url,
        items,
        items__ovps,
        items__ovps__vod_id,
        fields_to_expand=
        image_urls

episodes/epis_faae779b84ce4d1c91bd50bac5083036/
    ?fields=
        uid%2Ctitle%2Cself%2Cslug%2Ccreated%2Csynopsis%2Cvod_type_tag_urls%2Cvod_type_tag_urls__name%2Csessionoccurrence_urls%2Csessionoccurrence_urls__eventoccurrence_url%2Csessionoccurrence_urls__eventoccurrence_url__official_name%2Cimage_urls%2Cimage_urls__url%2Cvod_type_tag_urls%2Cvod_type_tag_urls__name%2Citems%2Citems__duration&fields_to_expand=vod_type_tag_urls%2Citems%2Cimage_urls%2Csessionoccurrence_urls%2Csessionoccurrence_urls__eventoccurrence_url


Social-Authenticate:


Identity-Provider:
identity_provider_url:"/api/identity-providers/iden_732298a17f9c458890a1877880d140f3/"


'''