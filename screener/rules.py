from utils import moving_average, percent_diff

        
def MA50gtMA150_rule(SMA50_value, SMA150_value, n_value_in):
    if SMA50_value > SMA150_value:
        SMA50_greater_SMA150_rule = True
        n_value = 2**n_value_in
        score = percent_diff(SMA50_value,SMA150_value)
    else:
        SMA50_greater_SMA150_rule = False
        n_value = 0.0
        score = 0.0
    return SMA50_greater_SMA150_rule, n_value, score

def MA150gtMA200_rule(SMA150_value, SMA200_value, n_value_in):
    if SMA150_value > SMA200_value:
        SMA150_greater_SMA200_rule = True
        n_value = 2**n_value_in
        score = percent_diff(SMA150_value,SMA200_value)
    else:
        SMA150_greater_SMA200_rule = False
        n_value = 0.0
        score = 0.0
    return SMA150_greater_SMA200_rule, n_value, score

def high_low_span_52_week_rule(week52_high, week52_low, n_value_in):
    if 0.75*week52_high > 1.25*week52_low:
        week52_span_rule = True
        n_value = 2**n_value_in
        score = percent_diff(0.75*week52_high, 1.25*week52_low)
    else:
        week52_span_rule = False
        n_value = 0.0
        score = 0.0
    return week52_span_rule, n_value, score

def rs_value_rule(RS_value, n_value_in):
    if RS_value > 1.0:
        rs_value_rule_ = True
        n_value = 2**n_value_in
        score = percent_diff(RS_value,1.0)
    else:
        rs_value_rule_ = False
        n_value = 0.0
        score = 0.0
    return rs_value_rule_, n_value, score
      
def liquidity_rule(SMA50_value, SMA50_volume_value, n_value_in):
    if SMA50_value*SMA50_volume_value <= 20e6:
        liquidity_rule_ = False
        n_value = 0
        score = percent_diff(20e6, SMA50_value*SMA50_volume_value)
    else:
        liquidity_rule_ = True
        n_value = 2**n_value_in
        score = 0.0
    return liquidity_rule_, n_value, score

def close_above_52weekhigh_rule(prev_close, week52_high, n_value_in):
    if prev_close > 0.75*week52_high:
        close_above_52weekhigh_rule_ = True
        n_value = 2**n_value_in
        score = percent_diff(prev_close, 0.75*week52_high)
    else:
        close_above_52weekhigh_rule_ = False
        n_value = 0.0
        score = 0.0
    return close_above_52weekhigh_rule_, n_value, score

def prev_close_rule(prev_close, n_value_in):
    if prev_close < 10:
        prev_close_rule_ = False
        n_value = 0.0
        score = 0.0
    else:
        prev_close_rule_ = True
        n_value = 2**n_value_in
        score = n_value
    return prev_close_rule_, n_value, score

def SMA200_slope_positive_rule(yahoo_df, ticker, days=21, n_value_in=5):
    SMA200_slope_positive_rule = True
    n_value = 2**n_value_in
    for day in range(days):
        curr_avg = moving_average(yahoo_df, days=200, delta=day)
        prev_avg = moving_average(yahoo_df, days=200, delta=day+1)
        score = percent_diff(curr_avg,prev_avg)
        if curr_avg >= prev_avg:
            continue
        else:
            SMA200_slope_positive_rule = False
            score = 0.0
            n_value = 0.0
    return SMA200_slope_positive_rule, percent_diff(curr_avg,prev_avg), n_value

def inst_ownership_rule(inst_own, n_value_in):
    if 0.05 <= inst_own:
        inst_ownership_rule_ = True
        score = percent_diff(inst_own, 0.05)
        n_value = 2**n_value_in
    else:
        inst_ownership_rule_ = False
        score = 0.0
        n_value = 0.0
    return inst_ownership_rule_, n_value, score

def close_greater_SMA50_rule(prev_close, SMA50_value, n_value_in):
    if prev_close > SMA50_value:
        close_greater_SMA50_rule_ = True
        n_value = 2**n_value_in
        score = percent_diff(prev_close,SMA50_value)
    else:
        close_greater_SMA50_rule_ = False
        n_value = 0.0
        score = 0.0
    return close_greater_SMA50_rule_, n_value, score

def sales_QoQ_yearly_rule(Sales_QoQ_percent, n_value_in):
    if Sales_QoQ_percent >= .25:
        sales_QoQ_yearly_rule_ = True
        n_value = 2**n_value_in
        score = percent_diff(Sales_QoQ_percent, 0.25)
    else:
        sales_QoQ_yearly_rule_ = False
        n_value = 0.0
        score = 0.0
    return sales_QoQ_yearly_rule_, n_value, score

def eps_QoQ_yearly_rule(EPS_QoQ_percent, n_value_in):   
    if EPS_QoQ_percent >= .18:
        eps_QoQ_yearly_rule_ = True
        n_value = 2**n_value_in
        score = percent_diff(EPS_QoQ_percent, 0.18)
    else:
        eps_QoQ_yearly_rule_ = False
        n_value = 0
        score = 0.0
    return eps_QoQ_yearly_rule_, n_value, score