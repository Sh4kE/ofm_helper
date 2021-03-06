import os

import numpy as np
import pandas as pd
from attrdict import AttrDict

from ofm_helper.common_settings import TRANSFERS_DIR


class TransferFilter(AttrDict):
    def __init__(self, *args, **kwargs):
        filterable_attributes = ['positions', 'ages', 'strengths', 'seasons', 'matchdays', 'min_price', 'max_price']
        super().__init__(*args, **kwargs)
        for attribute in filterable_attributes:
            if not hasattr(self, attribute):
                self[attribute] = None


class PandaManager:
    def __init__(self):
        self.data_frame = self._load_data()
        self.df_filterable_attributes = list(self.data_frame.columns.values)
        self.df_filterable_attributes.remove('Price')

    def get_data(self):
        if self.data_frame is None or self.data_frame.empty:
            self.data_frame = self._load_data()
        return self.data_frame

    def filter_transfers(self, transfer_filter=None):
        filtered_df = self.get_data().copy()

        if transfer_filter:
            for attribute in self.df_filterable_attributes:
                filtered_df = self._filter_for(filtered_df, transfer_filter, attribute)
            if transfer_filter.min_price:
                filtered_df = filtered_df[filtered_df.Price >= transfer_filter.min_price]
            if transfer_filter.max_price:
                filtered_df = filtered_df[filtered_df.Price <= transfer_filter.max_price]
            return filtered_df
        else:
            return self.data_frame

    @staticmethod
    def _filter_for(data_frame, transfer_filter, attribute):
        transfer_filter_attribute = str(attribute).lower() + 's'
        if transfer_filter[transfer_filter_attribute]:
            filtered_df = data_frame[data_frame[attribute].isin(transfer_filter[transfer_filter_attribute])]
            return filtered_df
        return data_frame

    def get_grouped_prices(self, group_by='Strength', **kwargs):
        df = self.filter_transfers(TransferFilter(**kwargs))
        return df.groupby(group_by).Price

    def _load_data(self):
        self.data_frame = pd.DataFrame()
        for file in os.listdir(TRANSFERS_DIR):
            if file.endswith('csv'):
                df = pd.read_csv(os.path.join(TRANSFERS_DIR, file),
                                 index_col=0,
                                 dtype={7: np.int32, 8: np.int32, 9: np.int32},
                                 skip_blank_lines=True,
                                 )
                df.drop(df.columns[[2, 3, 4]], axis=1, inplace=True)

                df = df.rename(columns={df.columns[0]: "Matchday",
                                        df.columns[1]: "Season",
                                        df.columns[2]: "Position",
                                        df.columns[3]: "Age",
                                        df.columns[4]: "Strength",
                                        df.columns[5]: "Price",
                                        })

                if self.data_frame.empty:
                    self.data_frame = df
                else:
                    self.data_frame = self.data_frame.append(df)

        return self.data_frame
