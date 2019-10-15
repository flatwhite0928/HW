# -*- coding: utf-8 -*-
import os
import sys
import csv
import datetime
import warnings
import pandas as pd
from datetime import timedelta, datetime
from tabulate import tabulate
from .promotion_module import Promotions
from .mapping_table import merchant_name_dict
from .user_product_module_v2 import UserProduct


warnings.filterwarnings("ignore")


class UserPromo:
    def __init__(self, xml_tree, docs_list):
        """
        Args:
            xml_tree: an xml type file
            docs_list: a list of three txt (json) files or False boolean values that need to be read
        """
        self.xml_tree = xml_tree
        self.docs_list = docs_list

    def _replace_values(self, promo_df, user_df):
        """
        Args:
            promo_df: a dataframe object of promotion info
            user_df: a dataframe object of user info

        Returns:
            two dataframe objects
        """
        # reverse the key and value for replacing merchant names
        reversed_dict = dict()
        for key in merchant_name_dict.keys():
            alt_names = merchant_name_dict[key]
            for name in alt_names:
                if not reversed_dict.get(name):
                    reversed_dict[name] = key

        # conduct the replacements
        for i in [1, 2, 3]:
            promo_df['promotiontype%s' % str(i)].replace({'Free Delivery': 'Free Shipping'}, inplace=True)

        user_df['product_retailer'].replace(reversed_dict, inplace=True)
        promo_df['advertisername'].replace(reversed_dict, inplace=True)

        return promo_df, user_df

    def _ranking_type_1(self, user_and_promo_df):
        """
        Args:
            user_and_promo_df: a dataframe object of user and promo info combined

        Returns:
            a dataframe object
        """
        user_and_promo_df = user_and_promo_df.reset_index().sort_values(['initiatorId', 'days_left', 'promotiontype1',
                                                                         'product_retailer', 'wish_list', 'tap_count',
                                                                         'view_count', 'product_price'],
                                                                        ascending=[True, True, False, True, False,
                                                                                   False, False, True]). \
            groupby(['initiatorId']).nth(0).reset_index().set_index(['initiatorId', 'product_retailer'])

        return user_and_promo_df

    def recommend_promo(self, sitewide=True, user_id=None, in_stock=False, min_left_day=0,
                        max_left_day=365, min_tap_count=0, in_wish_list=False):
        """
        Args:
            sitewide: a boolean value indicating whether only looking at sitewide promos; default = True
            user_id: a string or a list of strings of user ids to be filtered; default = None (i.e. all)
            in_stock: a boolean value indicating whether only looking at in stock items; default = False
            min_left_day: an integer indicating the minimum days left to be filtered; default = 0
            max_left_day: maximum days_left to be kept; default = 365; default = 365
            min_tap_count: a positive integer indicating the minimum tap count to be filtered; default = 0
            in_wish_list: a boolean value indicating whether only keeping items in wish list; default = False

        Returns:
            a dataframe object
        """
        # check type
        if not isinstance(sitewide, bool):
            raise TypeError('sitewide must be a boolean value')
        if not isinstance(min_tap_count, int):
            raise TypeError('min_tap_count must be an integer')
        else:
            if min_tap_count < 0:
                raise ValueError('min_tap_count must not be negative')
        if not isinstance(in_wish_list, bool):
            raise TypeError('in_wish_list must be a boolean value')

        # get promotion dataframe
        user_df = UserProduct(self.docs_list).get_all_info(user_id, in_stock)

        # get user dataframe
        if sitewide:
            promo_df = Promotions(self.xml_tree).apply_filter(min_left_day=min_left_day, max_left_day=max_left_day,
                                                              cat_names='default', promo_names='default',
                                                              wanted_words='default', unwanted_words='default')
        else:
            promo_df = Promotions(self.xml_tree).apply_filter(min_left_day=min_left_day, max_left_day=max_left_day)

        if len(promo_df) > 0 and len(user_df) > 0:
            # replace the column values
            promo_df, user_df = self._replace_values(promo_df, user_df)
            
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    
            promo_df.to_csv(open(BASE_DIR + '/data/all_promo.csv', 'w', newline='', encoding='utf-8'), index=False)

            # keep the first promotion info of each merchant-promotype combination
            promo_df = promo_df.sort_values(['advertisername', 'days_left'], ascending=[True, True]). \
                groupby(['advertisername', 'promotiontype1']).nth(0).reset_index()
                
            promo_df['advertisername'] = [i.lower() for i in promo_df['advertisername']]
            user_df['product_retailer'] = [i.lower() for i in user_df['product_retailer']]

            # merge user and promotion dataframes
            cols = ['advertisername', 'promotiontype1', 'duration (days)', 'offerdescription',
                    'offerenddate', 'offerstartdate', 'promotiontype2', 'promotiontype3', 'days_left']
            # if set(cols) <= set(promo_df.columns):
            user_and_promo_df = user_df.merge(promo_df.loc[:, cols],
                                              how='left', left_on='product_retailer', right_on='advertisername')

            # drop na rows
            user_and_promo_df = user_and_promo_df[(~user_and_promo_df['promotiontype1'].isna()) &
                                                  (~user_and_promo_df['initiatorId'].isna())]
            # drop Macy's
            user_and_promo_df = user_and_promo_df[user_and_promo_df['product_retailer'] != "macy's"]

            # set index
            user_and_promo_df = user_and_promo_df.sort_values(['initiatorId', 'promotiontype1', 'product_retailer',
                                                               'days_left', 'wish_list', 'tap_count', 'view_count',
                                                               'product_price'],
                                                              ascending=[True, False, True, True, False, False, False, True]).\
                set_index(['initiatorId', 'product_retailer', 'promotiontype1'])[
                ['product_id', 'product_name', 'tap_count', 'product_price', 'wish_list', 'view_count', 'product_in_stock',
                 'promotiontype2', 'promotiontype3', 'offerdescription', 'offerstartdate', 'offerenddate',
                 'days_left', 'product_image_url', 'product_purchase_url']]

            # apply optional filters
            user_and_promo_df = user_and_promo_df[user_and_promo_df['tap_count'] >= min_tap_count]
            if in_wish_list:
                user_and_promo_df = user_and_promo_df[user_and_promo_df['wish_list'] == 1]
            # user_and_promo_df.to_csv(open('./user_and_promo_df.csv', 'w', newline=''))
            # apply ranking
            result = self._ranking_type_1(user_and_promo_df)

            if len(result) > 0:
                # change types
                result['product_in_stock'] = result['product_in_stock'].astype(int)
                result['days_left'] = result['days_left'].astype(int)

                return result.reset_index()

        return pd.DataFrame(columns=['initiatorId', 'product_retailer', 'promotiontype1', 'product_id', 'product_name', 'tap_count',
                                     'product_price', 'wish_list', 'view_count', 'product_in_stock', 'promotiontype2', 'promotiontype3',
                                     'offerdescription', 'offerstartdate', 'offerenddate', 'days_left', 'product_image_url', 'product_purchase_url'])


def main(xml, doc1, doc2, doc3, doc4):
    #  read inputs
    # xml, doc1, doc2, doc3 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    # record_date = datetime.datetime.now().strftime('%F %H:%M:%S.%f')
    record_date = 'today'
    docs = [doc1, doc2, doc3, doc4]
    for d in docs:
        if d == "NA":
            docs[docs.index(d)] = False
    # get output
    result = UserPromo(xml, docs).recommend_promo(in_stock=True, sitewide=False)

    if len(result) == 0:
        print('no match')
    else:
        # compile and manipulate message
        result['message'] = result['promotiontype1'].str.upper() + ' now on ' + result['product_retailer'] + ' until ' + \
            result['offerenddate'].dt.strftime('%b %-d').astype(str) + '! Your favorite ' + result['product_name'] + \
            ' may qualify!'
        result['message'] = result.apply(manipulate_message, axis=1)

        # print results psql style
        # print(tabulate(result[['initiatorId', 'message']], headers='keys', tablefmt='psql'))

        # write log
        write_result_history(result, file_to_write='result_history.csv', record_date=record_date)

    return result


def manipulate_message(df):
    """
    Args:
        df: a dataframe object that contains column 'message'

    Returns:
        a pandas series object
    """
    message = df['message']
    # remove after-comma words
    try:
        ind = message.index(',')
        ind2 = message.index(' may qualify')
        message = message.replace(message[ind:ind2], '')
    except ValueError:
        pass
    # add emoji
    truck = '🚚'
    money = '💰'
    message = message.replace('FREE SHIPPING', '%s FREE SHIPPING %s' % (truck, truck))
    message = message.replace('PERCENTAGE OFF', '%s PERCENTAGE OFF %s' % (money, money))
    message = message.replace('DOLLAR OFF', '%sDOLLAR OFF%s' % (money, money))
    # show 'today' in message if necessary
    now_until_today = 'now until ' + pd.to_datetime('today').date().strftime('%b %d')
    end_today = 'ends today'
    message = message.replace(now_until_today, end_today)

    return message


def write_result_history(result, file_to_write, record_date='today'):
    """
    Args:
        result: a dataframe object
        file_to_write: a .csv file path
        record_date: a date string with year, e.g. 2019-07-12; default = 'today'
    """
    # add necessary columns
    result['ranking_type'] = '1'
    result['timestamp'] = datetime.now().strftime('%F %H:%M:%S.%f')
    result['message_date'] = pd.to_datetime(record_date).strftime('%m-%d-%Y')
    result['user_span_start_date'] = (pd.to_datetime(record_date) - timedelta(days=6)).strftime('%m-%d-%Y')
    # if first time, write file
    if not os.path.isfile(file_to_write):
        result.to_csv(file_to_write, index=False)
    # if not, add to file
    else:
        with open(file_to_write, 'a', newline='', encoding='utf-8') as f:
            outwriter=csv.writer(f)
            outwriter.writerow([])
            result.to_csv(f, header=False, index=False)
    return

