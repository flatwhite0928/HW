import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET


class Promotions:
    def __init__(self, xml_tree):
        self.xml_tree = xml_tree

    def _xml_to_df(self):
        """
        Returns:
            a pandas dataframe object
        """
        # parse xml tree
        parsed_xml = ET.parse(self.xml_tree)

        # define column names
        promo_df_cols = ['category1', 'category2', 'category3', 'promotiontype1', 'promotiontype2', 'promotiontype3',
                         'offerdescription', 'couponcode', 'couponrestriction', 'offerstartdate', 'offerenddate',
                         'clickurl', 'advertiserid', 'advertisername', 'network']

        # create empty dict
        result_dict = {name:list() for name in promo_df_cols}

        # append element texts
        for node in parsed_xml.getroot():
            if node.tag == 'link':
                # 3 possible categories
                category_list = [np.nan] * 3
                for i in range(len(node.find('categories'))):
                    category_list[i] = node.find('categories')[i].text
                result_dict['category1'].append(category_list[0])
                result_dict['category2'].append(category_list[1])
                result_dict['category3'].append(category_list[2])
                # 3 possible promotion types
                ptype_list = [np.nan] * 3
                for i in range(len(node.find('promotiontypes'))):
                    ptype_list[i] = node.find('promotiontypes')[i].text
                result_dict['promotiontype1'].append(ptype_list[0])
                result_dict['promotiontype2'].append(ptype_list[1])
                result_dict['promotiontype3'].append(ptype_list[2])
                # columns that definitely exist
                result_dict['offerdescription'].append(node.find('offerdescription').text)
                result_dict['offerstartdate'].append(node.find('offerstartdate').text)
                result_dict['offerenddate'].append(node.find('offerenddate').text)
                result_dict['advertiserid'].append(node.find('advertiserid').text)
                result_dict['advertisername'].append(node.find('advertisername').text)
                result_dict['network'].append(node.find('network').text)
                # columns that may exist
                try:
                    result_dict['clickurl'].append(node.find('clickurl').text)
                except AttributeError:
                    result_dict['clickurl'].append(np.nan)
                try:
                    result_dict['couponcode'].append(node.find('couponcode').text)
                except AttributeError:
                    result_dict['couponcode'].append(np.nan)
                try:
                    result_dict['couponrestriction'].append(node.find('couponrestriction').text)
                except AttributeError:
                    result_dict['couponrestriction'].append(np.nan)

        promo_df = pd.DataFrame(result_dict)

        # fix typo
        promo_df['category2'].replace({'Jewellery & Accessories': 'Jewelry & Accessories'}, inplace=True)
        promo_df['category3'].replace({'Jewellery & Accessories': 'Jewelry & Accessories'}, inplace=True)

        return promo_df

    # default list parameters
    default_categories = ['Shoes', 'Apparel', "Apparel - Woman’s", "Apparel - Men’s",
                          "Apparel - Babies & Kids", "Jewelry & Accessories"]
    default_promotions = ['Percentage off', 'Dollar off', 'Gift with Purchase', 'Buy One / Get One',
                          'Free Shipping', 'Combination Savings', 'Pounds amount off', 'Free Delivery']
    default_wanted = ['sitewide', 'everything', 'all order', 'all purchase', 'all style',
                      'all design', 'free ship', 'free deliver', 'on order', 'free return']
    default_unwanted = ['almost everything', 'almost all', 'almost entire', 'exclu', 'not inclu']

    def apply_filter(self, min_left_day=0, max_left_day=365, merchant=None, **kwargs):
        """
        Args:
            min_left_day: minimum days_left to be kept; default = 0
            max_left_day: maximum days_left to be kept; default = 365
            merchant: a str or a list of merchant name(s) to be filtered
            **kwargs:
                cat_names: a list of category name strings we want to keep; value 'default' = list above
                promo_names: a list of promotion type strings we want to keep; value 'default' = list above
                wanted_words: a list of keywords that we want to keep; value 'default' = list above
                unwanted_words: a list of keywords that we don't want to keep; value 'default' = list above

        Returns:
            a filtered dataframe object
        """
        # check types of parameters
        if merchant:
            if isinstance(merchant, str):
                pass
            elif isinstance(merchant, list):
                if all(isinstance(m, str) for m in merchant):
                    pass
            else:
                raise TypeError('merchant must be a string or a list of strings')

        if kwargs:
            for key in kwargs.keys():
                if key not in {'cat_names', 'promo_names', 'wanted_words', 'unwanted_words'}:
                    raise KeyError('Unknown parameter %s' % str(key))
                if kwargs[key] != 'default':
                    if not isinstance(kwargs[key], list):
                        raise TypeError('%s must be a list' % str(key))
        try:
            min_left_day = int(min_left_day)
        except TypeError:
            raise TypeError('min_left_day must be a number')
        try:
            max_left_day = int(max_left_day)
        except:
            raise TypeError('max_left_day must be a number')

        # obtain the raw dataframe
        df = self._xml_to_df()

        # convert to datetime value
        df['offerstartdate'] = pd.to_datetime(df['offerstartdate'])
        df['offerenddate'] = pd.to_datetime(df['offerenddate'])

        # compute days left and filter by days left
        df['days_left'] = df['offerenddate'].apply(lambda x: (x.date() - pd.to_datetime('today').date()).days)
        df = df[df['days_left'] >= min_left_day]
        df = df[df['days_left'] <= max_left_day]
        
        df = df.fillna('')
        # filter by merchant
        if merchant:
            if isinstance(merchant, str):
                df = df[df['advertisername'] == merchant]
            elif isinstance(merchant, list):
                df = df[df['advertisername'].isin(merchant)]

        # filter by category
        if 'cat_names' in kwargs:
            if kwargs['cat_names'] == 'default':
                df = df[(df.iloc[:, :3].isin(self.default_categories)).any(axis=1)]
            else:
                df = df[(df.iloc[:, :3].isin(kwargs['cat_names'])).any(axis=1)]

        # filter by promotion type
        if 'promo_names' in kwargs:
            if kwargs['promo_names'] == 'default':
                df = df[df.iloc[:,3].isin(self.default_promotions)]
            else:
                df = df[df.iloc[:,3].isin(kwargs['promo_names'])]

        # filter by wanted keywords
        if 'wanted_words' in kwargs:
            if kwargs['wanted_words'] == 'default':
                df = df[df['offerdescription'].str.contains('|'.join(self.default_wanted),
                                                            case=False, regex=True)]
            else:
                df = df[df['offerdescription'].str.contains('|'.join(kwargs['wanted_words']),
                                                            case=False, regex=True)]

        # filter by unwanted keywords
        if 'unwanted_words' in kwargs:
            if kwargs['unwanted_words'] == 'default':
                df = df[~df['offerdescription'].str.contains('|'.join(self.default_unwanted),
                                                             case=False, regex=True)]
            else:
                df = df[~df['offerdescription'].str.contains('|'.join(kwargs['unwanted_words']),
                                                             case=False, regex=True)]

        return df.reset_index(drop=True)
