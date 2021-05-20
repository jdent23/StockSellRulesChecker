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
      search_options: {}
    };

    this.setSearchOptions = function(new_search_options) {
      this.setState({search_options: new_search_options})
    }.bind(this);
  }

  modifyData = function(value) {
    if(value.toString() === "true") {
      return  <th style={{background: "green"}}>True</th>
    } else if(value.toString() === "false") {
      return <th style={{background: "red"}}>False</th>
    } else {
      return <th>{value.toString()}</th>
    }
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
                <TableTitles columns={this.state.market_columns} notifyRule={this.props.notifyRule}/>
                <div className="MarketData">
                    <TableData modifyData={this.modifyData} data={this.state.market_data.filter((data_row) => ApplyFilter(this.state.market_columns, data_row, this.state.search_options))}/>
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