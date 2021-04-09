import pandas as pd
import numpy as np

class ScreenComparer:
    @staticmethod
    def enter_exit_rule(row, col, df1, df2):
        print(type(row))

    @staticmethod
    def compare_pd(df1, df2, cols):
        df1_tickers = df1['Ticker'].to_list()
        df2_tickers = df2['Ticker'].to_list()

        diff_tickers_1 = list(set(df1_tickers) - set(df2_tickers)) 
        diff_tickers_2 = list(set(df2_tickers) - set(df1_tickers)) 
        diff_tickers = diff_tickers_1 + diff_tickers_2
        
        df_same_1 = df1[~df1['Ticker'].isin(diff_tickers)]
        df_same_2 = df2[~df2['Ticker'].isin(diff_tickers)]
        df_diff_1 = df1[df1['Ticker'].isin(diff_tickers)]
        df_diff_2 = df2[df2['Ticker'].isin(diff_tickers)]

        df_same_2 = df_same_2.set_index('Ticker')
        df_same_2 = df_same_2.reindex(index=df_same_1['Ticker'])
        df_same_2 = df_same_2.reset_index()
        df_same_2 = df_same_2.replace({'False': False, 'True': True})

        df_same_1 = df_same_1.set_index('Ticker')
        df_same_1 = df_same_1.reindex(index=df_same_2['Ticker'])
        df_same_1 = df_same_1.reset_index()
        df_same_1 = df_same_1.replace({'False': False, 'True': True})

        df_out = df_same_1[['Ticker','N-Value Rating']]
        
        # Find changes in existing stocks
        for col in cols:
            col_temp = col.replace(" (1st)", "").replace(" (2nd)","")
            df_out['{} Different?'.format(col_temp)] = np.where(df_same_1[col] != df_same_2[col], 'True', 'False')
            
            df_out['{} Entered/Exited Rule?'.format(col_temp)] = np.where(df_same_1[col] < df_same_2[col], 'Entered Rule', np.where(df_same_1[col] > df_same_2[col], 'Exited Rule', 'Did Not Change'))

        # Add stocks that do not exist if df2
        cols = df_out.columns
        for _, row in df_diff_1.iterrows():
            new_row = []
            for col in cols:
                new_row.append(True)
        temp_series = pd.Series(new_row, index = df_out.columns)
        df_out = df_out.append(temp_series, ignore_index=True)

        # Add stocks that do not exist if df1
        for _, row in df_diff_2.iterrows():
            new_row = []
            for col in cols:
                new_row.append(True)
        temp_series = pd.Series(new_row, index = df_out.columns)
        df_out = df_out.append(temp_series, ignore_index=True)

        df_out = df_out.replace({'False': False, 'True': True})
        
        to_drop = ['Ticker', 'N-Value Rating']
        for col in cols:
            if "Entered/Exited Rule?" in col:
                to_drop.append(col)

        df_out = df_out[df_out.drop(to_drop, axis=1).any(axis=1)]
        return df_out

    @staticmethod
    def compare_screen(old_screen, new_screen):
        old_screen_df = pd.read_csv(old_screen)
        new_screen_df = pd.read_csv(new_screen)
        cols = old_screen_df.columns
        print(cols)
        rule_cols = ['Ticker', 'N-Value Rating'] + [col for col in cols if "rule" in col and "score" not in col and "nvalue" not in col] 

        old_screen_rules_df = old_screen_df[rule_cols]
        new_screen_rules_df = new_screen_df[rule_cols]

        diff_df = ScreenComparer.compare_pd(old_screen_rules_df, new_screen_rules_df, rule_cols)
        diff_df = diff_df.sort_values(by=['N-Value Rating'], ascending=False)
        diff_df.to_csv("screener_comparison.csv")

if __name__ == "__main__":
  comparer = ScreenComparer()
  comparer.compare_screen("screener_results_2021_4_8.csv","screener_results_2021_4_9.csv")
