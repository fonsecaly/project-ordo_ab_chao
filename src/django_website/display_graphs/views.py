from django.shortcuts import render
from ebaysdk.finding import Connection as finding
import xmltodict
from json import loads, dumps
import pandas as pd
import numpy as np
import datetime

content_df = pd.DataFrame()

def display_the_graphs(request):
    keywords = request.POST.get('search')
    api = finding(appid='JohnHein-homepage-PRD-392e94856-07aba7fe', config_file=None, siteid='EBAY-US')
    api_request = {'keywords':keywords, 'itemFilter':[{'name':'SoldItemsOnly', 'value':True},],'outputSelector':['SellerInfo']}
    response = api.execute('findCompletedItems', api_request)
    content = response.content
    xml_dict = xmltodict.parse(content)
    content_dict = to_dict(xml_dict)
    count = content_dict['findCompletedItemsResponse']['searchResult']['@count']
    item_dict = content_dict['findCompletedItemsResponse']['searchResult']['item']
    print('count:', count)
    print('\nitem_dict:\n', item_dict)
    content_df = extract_values(item_dict)
    y_values = content_df['endPrice'].tolist()
    y_values = [float(i) for i in y_values]
    x_values_b = content_df['endTime'].tolist()
    x_values = convert_datetime(x_values_b)
    #print('\nx_values: ', x_values,'\n')
    #print('\ny_values: ', y_values,'\n')
    #print('\nx_values count:', len(x_values),'\n')
    #print('\ny_values count:', len(y_values),'\n')
    #print('\nx_values type:', type(x_values[-1]),'\n')
    #print('\ny_values type:', type(y_values[-1]),'\n')
    chart1_data = [list(i) for i in zip(x_values, y_values)]
    #print('chart1 data:', chart1_data)
    context = {
        'response': content_df.to_html(),
        'content_df': content_df,
        'chart1': chart1_data
    }
    return render(request, 'display_graphs/graphs.html', context)

def to_dict(input_ordered_dict):
    return loads(dumps(input_ordered_dict))

def extract_values(temp_dict):
    df = pd.DataFrame(columns=['itemId','title','endPrice','shippingServiceCost','bidCount','watchCount','returnsAccepted','location','endTime','startTime','handlingTime','sellerUserName','feedbackScore','positiveFeedbackPercent','topRatedSeller'])
    a,b,c,d,e,f,g,h,i,j,k,l,m,n,o = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
    #print('\ntype of data:\n', type(temp_dict))
    length = len(temp_dict)
    #print('\nlength:\n', length)
    for index in range(length):
        for key, value in temp_dict[index].items():
            #print('temp_dict[index][key]:', key)
            if key == 'itemId':
                a.append(value)
            if key == 'title':
                b.append(value)
            if key == 'sellingStatus':
                c.append(temp_dict[index]['sellingStatus']['convertedCurrentPrice']['#text'])
                try:
                    d.append(temp_dict[index]['sellingStatus']['bidCount'])
                except KeyError:
                    d.append(np.nan)
            if key == 'shippingInfo':
                e.append(temp_dict[index]['shippingInfo']['handlingTime'])
                try:
                    m.append(temp_dict[index]['shippingInfo']['shippingServiceCost']['#text'])
                except KeyError:
                    m.append(np.nan)
            if key == 'sellerInfo':
                f.append(temp_dict[index]['sellerInfo']['sellerUserName'])
                g.append(temp_dict[index]['sellerInfo']['feedbackScore'])
                h.append(temp_dict[index]['sellerInfo']['positiveFeedbackPercent'])
                n.append(temp_dict[index]['sellerInfo']['topRatedSeller'])
            if key == 'location':
                i.append(value)
            if key == 'listingInfo':
                j.append(temp_dict[index]['listingInfo']['endTime'])
                l.append(temp_dict[index]['listingInfo']['startTime'])
                try:
                    k.append(temp_dict[index]['listingInfo']['watchCount'])
                except KeyError:
                    k.append(np.nan)
            if key == 'returnsAccepted':
                o.append(value)

    df = pd.DataFrame({'itemId':pd.Series(a),'title':pd.Series(b),'endPrice':pd.Series(c),'shippingServiceCost':pd.Series(m),
                       'bidCount':pd.Series(d),'watchCount':pd.Series(k),'returnsAccepted':pd.Series(o),
                       'location':pd.Series(i),'endTime':pd.Series(j),'startTime':pd.Series(l),'handlingTime':pd.Series(e),
                       'sellerUserName':pd.Series(f),'feedbackScore':pd.Series(g),'positiveFeedbackPercent':pd.Series(h),
                       'topRatedSeler':pd.Series(n)})  
    #print('\ndf:\n', df)
    #print('\narray a:\n', a)
    #print('\narray b:\n', b)
    #print('\narray c:\n', c)
    #print('\narray d:\n', d)
    #print('\narray f:\n', f)
    df['endTime'] = pd.to_datetime(df['endTime']) # datetime ISO 8601 format ---> YYYY-MM-DD HH:MM:SS +HH:MM (NOTE: '+HH:MM' is UTC offset)
    df['endTimeOfDay'],df['endDate'] = df['endTime'].apply(lambda x:x.time()),df['endTime'].apply(lambda x:x.date())
    return df

def convert_datetime(arr):
    arr2 = []
    for i in arr:
        dateobj = str(i)
        dateobj = dateobj[:19]
        arr2.append(int(datetime.datetime.strptime(dateobj, "%Y-%m-%d %H:%M:%S").timestamp())*1000)
        #print('convert_datetime ',arr2[-1])
        #print('dateobj:', dateobj)
    return arr2
