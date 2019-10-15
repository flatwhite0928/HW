import os
import json
import psycopg2
import pandas as pd

# filter by id at first
class UserProduct:
    def __init__(self, docs_list):
        """
        Args:
            docs_list: a list of three txt (json) files or False boolean values that need to be read
        """
        # check type
        if not isinstance(docs_list, list):
            raise TypeError('docs_list must be a list')
        else:
            if len(docs_list) != 4:
                raise ValueError('docs_list must have 4 elements')
            for doc in docs_list:
                if doc:
                    if not os.path.isfile(doc):
                        raise FileNotFoundError("One or more docs don't exist")
        self.tbb_txt = docs_list[0]
        self.wl_txt = docs_list[1]
        self.remove_txt = docs_list[2]
        self.vp_txt = docs_list[3]

    default_drop_cols = ['app_build_number', 'app_version_string', 'carrier', 'lib_version',
                         'os_version', 'model', 'radio', 'os', 'wifi', 'screen_height', 'screen_width',
                         'initiatorAccountType', 'mp_lib', 'mp_processing_time_ms', 'insert_id', 'device',
                         'device_id', 'appVersion', 'product_alt_image_url_1', 'product_alt_image_url_2',
                         'product_alt_image_url_3', 'product_sale_price_range_label', 'kaloRep']

    def _json_to_df(self, doc, drop_col=default_drop_cols, user_id=None):
        """
        Args:
            doc: a txt (json) file that needs to be converted
            drop_col: a list of dataframe column names that need to be dropped; default = list above
            user_id: a str or a list that represents one or multiple user ids to be shown

        Returns:
            a dataframe object
        """
        # check type
        if isinstance(user_id, str):
            user_id = [user_id]
        if not isinstance(drop_col, list):
            raise TypeError('drop_col must be a list')

        # read txt
        with open(doc, 'r') as f:
            data_txt = json.load(f, encoding='utf-8')
        # data_txt = [i.strip() for i in data_txt]

        # write json into dataframe
        df = pd.DataFrame(columns=[])
        if user_id:
            for i in range(len(data_txt)):
                if data_txt[i]['properties'].get('initiatorId'):
                    current_id = data_txt[i]['properties'].get('initiatorId')
                    if current_id in user_id:
                        df = df.append(data_txt[i]['properties'], ignore_index=True)
        # if user_id not provided, append all
        else:
            for i in range(len(data_txt)):
                df = df.append(data_txt[i]['properties'], ignore_index=True)

        # rename columns
        for col in df.columns:
            if '$' in col:
                df.rename(columns={col: col.replace('$', '')}, inplace=True)
            elif '__' in col:
                df.rename(columns={col: col.replace('__', '_')}, inplace=True)

        # drop unwanted columns
        drop_col = set(drop_col).intersection(set(df.columns))
        df.drop(columns=drop_col, inplace=True)

        # remove NA rows
        if 'product_price' in df.columns:
            df = df[~df['product_price'].isna()]
        if 'product_retailer' in df.columns:
            df = df[~df['product_retailer'].isna()]
        if 'initiatorId' in df.columns:
            df = df[~df['initiatorId'].isna()]

        return df.reset_index(drop=True)

    def _get_real_wl(self, wl_df, remove_df):
        """
        Args:
            wl_df: a dataframe object that contains information of "add to wish list"
            remove_df: a dataframe object that contains information of "remove from wish list"

        Returns:
            a dataframe object
        """
        # dummy columns to help recognize whether removed
        remove_df['remove'] = 1
        wl_df['wl'] = 1
        remove_df.rename(columns={'productId': 'product_id'}, inplace=True)
        # if remove_df exists
        if all(Id in remove_df.columns for Id in ['initiatorId', 'product_id', 'time', 'remove']):
            wl_with_remove = pd.concat([wl_df, remove_df[['initiatorId', 'product_id', 'time', 'remove']]])
        # if remove_df not exists
        else:
            wl_with_remove = wl_df

        wl_with_remove = wl_with_remove.sort_values(['initiatorId', 'product_id', 'time'],
                                                    ascending=[True, True, False]). \
            groupby(['initiatorId', 'product_id']).nth(0)
        # get rid of entries that are removed from wish list
        wl_with_remove = wl_with_remove[wl_with_remove['remove'] != 1].reset_index()

        return wl_with_remove

    def _aggregate_tbb(self, tbb_df):
        """
        Args:
            tbb_df: a dataframe object that contains information of "tap buy button"

        Returns:
            a dataframe object
        """
        # group by important features
        tbb_grouped = pd.DataFrame(tbb_df.groupby(['initiatorId', 'product_retailer',
                                                   'product_name', 'product_id']).
                                   size().sort_values(ascending=False)).reset_index()

        # merge price and in_stock info
        prod_price = pd.DataFrame(tbb_df.groupby('product_id').mean()['product_price'])
        prod_stock = pd.DataFrame(tbb_df.groupby('product_id').nth(0)['product_in_stock'])
        prod_url = pd.DataFrame(tbb_df.groupby('product_id').nth(0)['product_purchase_url'])
        prod_image = pd.DataFrame(tbb_df.groupby('product_id').nth(0)['product_image_url'])
        tbb_grouped = tbb_grouped.join(prod_price, on='product_id')
        tbb_grouped = tbb_grouped.join(prod_stock, on='product_id')
        tbb_grouped = tbb_grouped.join(prod_url, on='product_id')
        tbb_grouped = tbb_grouped.join(prod_image, on='product_id')
        tbb_grouped.rename(columns={0: 'tap_count'}, inplace=True)

        return tbb_grouped.reset_index(drop=True)
        
    def getinfo(self, id):
        conn = psycopg2.connect("dbname=d1k0np1ud1m0la user=u4cutqdth0kekl "
                                "password=p9e44f382b73600c2595f348394b42eb0d3c4ad7c43d7c08e8bd2a94e80e9c0e7 "
                                "host=ec2-34-194-148-74.compute-1.amazonaws.com")
        cur = conn.cursor()
        re = []
        for i in id:
            cur.execute("select retailer, name, price, in_stock, purchase_url, image_url from jacl_app_product where id='{}';".format(i))
            result = cur.fetchall()
            if result:
                re.append(list(result[0]))
            else:
                re.append(['']*6)
        view = pd.DataFrame(re)
        view.columns = ['product_retailer', 'product_name', 'product_price', 'product_in_stock',
                             'product_purchase_url', 'product_image_url']
        return(view)

    def get_all_info(self, user_id=None, in_stock=False):
        """
        Args:
            user_id: a str or a list that represents one or multiple user ids to be shown
            in_stock: a boolean value indicating whether to keep only in stock items

        Returns:
            a dataframe object
        """
        # check type
        if user_id:
            if isinstance(user_id, str):
                pass
            elif isinstance(user_id, list):
                if all(isinstance(uid, str) for uid in user_id):
                    pass
            else:
                raise TypeError('user_id must be a string or a list of strings')
        if not isinstance(in_stock, bool):
            raise TypeError('in_stock must be a boolean value')

        # generate dataframes
        if self.tbb_txt:
            tbb_df = self._json_to_df(self.tbb_txt, user_id=user_id)
        else:
            tbb_df = pd.DataFrame(columns=[])
        if self.wl_txt:
            wl_df = self._json_to_df(self.wl_txt, user_id=user_id)
        else:
            wl_df = pd.DataFrame(columns=[])
        if self.remove_txt:
            remove_df = self._json_to_df(self.remove_txt, user_id=user_id)
        else:
            remove_df = pd.DataFrame(columns=[])
        if self.vp_txt:
            vp_df = self._json_to_df(self.vp_txt, user_id=user_id)
        else:
            vp_df = pd.DataFrame(columns=[])

        # get real wish list
        if len(remove_df) > 0 and len(wl_df) > 0:
            real_wl = self._get_real_wl(wl_df, remove_df)
        elif len(remove_df) == 0 and len(wl_df) > 0:
            real_wl = wl_df
        # if both wl_df and remove_df empty, create empty df with desired column names
        else:
            real_wl = pd.DataFrame(columns=['initiatorId', 'product_id', 'product_price',
                                            'product_retailer', 'product_name', 'product_in_stock',
                                            'product_purchase_url', 'product_image_url'])

        # aggregate tbb_df
        if len(tbb_df) > 0:
            tbb_grouped = self._aggregate_tbb(tbb_df)
        # if tbb_df empty, create empty df with desired column names
        else:
            tbb_grouped = pd.DataFrame(columns=['initiatorId', 'product_retailer', 'product_name', 'product_id',
                                                'tap_count', 'product_price', 'product_in_stock', 'wish_list',
                                                'product_purchase_url', 'product_image_url'])

        if len(vp_df) > 0:
            vp_df.rename(columns={'productId': 'product_id'}, inplace=True)
            vp_grouped = pd.DataFrame(vp_df.groupby(['initiatorId', 'product_id']).size().sort_values(ascending=False)).reset_index()
            view = self.getinfo(vp_grouped['product_id'])
            newview = pd.concat([vp_grouped, view], axis=1)     
            newview.rename(columns={0: 'view_count'}, inplace=True)
        else:
            newview = pd.DataFrame(columns=['initiatorId', 'product_id', 'view_count', 'product_retailer', 'product_name', 
                                            'product_price', 'product_in_stock', 'product_purchase_url', 'product_image_url'])
                                          
        # merge them
        both_df = tbb_grouped.merge(real_wl[['initiatorId', 'product_id', 'product_price',
                                             'product_retailer', 'product_name', 'product_in_stock',
                                             'product_purchase_url', 'product_image_url']],
                                    how='outer', on=['initiatorId', 'product_id'])
        # wish list binary
        both_df.loc[((both_df.iloc[:, 9:15].isna()).all(axis=1)), 'wish_list'] = 0
        both_df['wish_list'] = both_df['wish_list'].fillna(1).astype(int)

        # further cleaning
        col_names = ['product_retailer', 'product_name', 'product_price', 'product_in_stock',
                     'product_purchase_url', 'product_image_url']
        for col in col_names:
            both_df[col + '_x'] = both_df[col + '_x'].fillna(both_df[col + '_y'])
        both_df.drop(columns=[c + '_y' for c in col_names], inplace=True)

        # rename cols
        for col in both_df.columns:
            if '_x' in col:
                both_df.rename(columns={col: col.replace('_x', '')}, inplace=True)
                
        td = both_df.merge(newview, how='outer', on=['initiatorId', 'product_id'])
        td['wish_list'] = td['wish_list'].fillna(0).astype(int)
        td['view_count'] = td['view_count'].fillna(0).astype(int)
        td['tap_count'] = td['tap_count'].fillna(0).astype(int)
        for col in col_names:
            td[col + '_x'] = td[col + '_x'].fillna(td[col + '_y'])
        td.drop(columns=[c + '_y' for c in col_names], inplace=True)
        for col in td.columns:
            if '_x' in col:
                td.rename(columns={col: col.replace('_x', '')}, inplace=True)

        # filter by whether in stock
        if in_stock:
            td = td[td['product_in_stock'] == 1]
        
        td['product_image_url'] = ['https://kalo-production.s3.amazonaws.com/' + i if 'kalo' not in i else i for i in td['product_image_url']]
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    
        td.reset_index(drop=True).to_csv(open(BASE_DIR + '/data/all_event.csv', 'w', newline=''))
        
        return td.reset_index(drop=True)
        