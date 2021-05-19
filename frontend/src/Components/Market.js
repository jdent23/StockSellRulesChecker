import React, { Component } from 'react';
import { TableTitles } from './TableTitles';
import { TableData } from './TableData';
import { SearchOptions } from './SearchOptions';
import { ApplyFilter } from './SearchOptions';

export class Market extends Component {
  constructor(props) {
    super(props);
    this.state = {
      market_columns: [],
      market_data: [[]],
      filtered_data: [[]],
      search_options: null
    };

    this.setSearchOptions = function(new_search_options) {
      this.setState({search_options: new_search_options})
      console.log("Parent state options")
      console.log(new_search_options);
      
      this.state.filtered_data = this.state.market_data.filter((data_row) => ApplyFilter(this.state.market_columns, data_row, new_search_options));
      window.location.replace("http://www.w3schools.com");
    }.bind(this);
  }

  componentDidMount() {
    this.setState({ isLoading: true });
 
    fetch("http://localhost:5000/api/market")
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(res => this.setState({ market_columns: res.market_columns, market_data: res.market_data, filtered_data: res.market_data}))
      .catch(error => this.setState({ error }));
  }



  render() {

    return <div className="MarketComp">
        <div className="Market">
            <div className="MarketTable">
                <TableTitles columns={this.state.market_columns}/>
                <div className="MarketData">
                    <TableData data={this.state.filtered_data}/>
                </div>
            </div>
        </div>

        <form action="http://localhost:5000/export_table" method="get">
              <input type="submit" value="Download Table"/>
        </form>
        <SearchOptions option_names={this.state.market_columns}
                      data_types={this.state.market_data[0].map(value => typeof(value))}
                      set_search_options={this.setSearchOptions}/>
    </div>
  }
}