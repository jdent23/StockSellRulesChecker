import React, { Component } from 'react';
import { TableTitles } from './TableTitles';
import { TableData } from './TableData';

export class MarketDirection extends Component {
  constructor(props) {
    super(props);
    this.state = {
      date: "",
      market_direction: "",
      market_direction_columns: [],
      market_direction_data: [[]]
    };
  }

  componentDidMount() {
    this.setState({ isLoading: true });
 
    fetch("http://localhost:5000/api/market_direction")
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(res => this.setState({ date: res.date_string, market_direction: res.market_direction, market_direction_columns: res.market_direction_columns, market_direction_data: res.market_direction_data}))
      .catch(error => this.setState({ error }));
  }

  render() {

    var market_direction_summary_background = "yellow"
    if(this.state.market_direction === "Upward") {
      market_direction_summary_background = "green"
    } else if(this.state.market_direction === "Downward") {
      market_direction_summary_background = "red"
    }

    return <div className="MarketDirectionComp">
      <div style={{background: "black"}}>
        <div className="MarketDirectionSummary" style={{background: market_direction_summary_background}}>
          <h3>{this.state.date} Direction: {this.state.market_direction}</h3>
        </div>
          <TableTitles columns={this.state.market_direction_columns}/>
          <TableData data={this.state.market_direction_data}/>
      </div>
      <h2>Please Donate to Keep<br></br>This Webpage Active!</h2>
      <form action="https://www.paypal.com/donate" method="post" target="_top">
        <input type="hidden" name="business" value="EAL2W358H6JKG" />
        <input type="hidden" name="item_name" value="Stock Screener" />
        <input type="hidden" name="currency_code" value="USD" />
        <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
        <img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1" />
      </form>
    </div>
  }
}