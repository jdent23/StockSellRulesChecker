import React, { Component } from 'react';
import { TableTitles } from './TableTitles';
import { TableData } from './TableData';
import { SearchOptions } from './SearchOptions';
import { ApplyFilter } from './SearchOptions';

export class Comparison extends Component {
  constructor(props) {
    super(props);
    this.state = {
      comparison_columns: [],
      comparison_data: [[]],
      search_options: {}
    };

    this.setSearchOptions = function(new_search_options) {
      this.setState({search_options: new_search_options});
    }.bind(this);
  }

  componentDidMount() {
    this.setState({ isLoading: true });
 
    fetch("http://localhost:5000/api/comparison")
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(res => this.setState({ comparison_columns: res.comparison_columns, comparison_data: res.comparison_data, filtered_data: res.comparison_data}))
      .catch(error => this.setState({ error }));
  }

  modifyData = function(value) {
    if(value === 1) {
      return  <th style={{background: "green"}}>True</th>
    } else if(value === 0) {
      return  <th>None</th>
    } else if(value === -1) {
      return <th style={{background: "red"}}>False</th>
    } else {
      return <th>{value.toString()}</th>
    }
  }



  render() {

    return <div className="ComparisonComp">
        <div className="Comparison">
            <div className="ComparisonTable">
                <TableTitles columns={this.state.comparison_columns} notifyRule={this.props.notifyRule}/>
                <div className="ComparisonData">
                    <TableData modifyData={this.modifyData} data={this.state.comparison_data.filter((data_row) => ApplyFilter(this.state.comparison_columns, data_row, this.state.search_options))}/>
                </div>
            </div>
        </div>

        <form action="http://localhost:5000/export_comparison_table" method="get">
              <input type="submit" value="Download Table"/>
        </form>
        <SearchOptions option_names={this.state.comparison_columns}
                      data_types={this.state.comparison_data[0].map(value => typeof(value))}
                      set_search_options={this.setSearchOptions}/>
    </div>
  }
}