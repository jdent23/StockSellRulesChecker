import pandas as pd
import numpy as np

class ScreenComparer:

    @staticmethod
    def diff_pd(df1, df2, df_ticker, cols):
        df_out = df_ticker
        for col in cols:
            col_temp = col.replace(" (1st)", "").replace(" (2nd)","")
            df_out['{} Different?'.format(col_temp)] = np.where(df1[col] != df2[col], 'True', 'False')
        return df_out

    @staticmethod
    def compare_screen(old_screen, new_screen):
        old_screen_df = pd.read_csv(old_screen)
        new_screen_df = pd.read_csv(new_screen)
        cols = old_screen_df.columns
        rule_cols = [col for col in cols if "rule" in col]

        old_screen_rules_df = old_screen_df[rule_cols]
        new_screen_rules_df = new_screen_df[rule_cols]

        diff_df = ScreenComparer.diff_pd(old_screen_rules_df, new_screen_rules_df, new_screen_df[['Ticker']], rule_cols)
        diff_df.to_csv("screener_comparison.csv")

if __name__ == "__main__":
  comparer = ScreenComparer()
  comparer.compare_screen("screener_results_prev.csv","screener_results.csv")
