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
      filtered_data: [[]],
      search_options: null
    };

    this.setSearchOptions = function(new_search_options) {
      this.setState({search_options: new_search_options})
      console.log("Parent state options")
      console.log(new_search_options);
      
      this.state.filtered_data = this.state.comparison_data.filter((data_row) => ApplyFilter(this.state.comparison_columns, data_row, new_search_options));
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



  render() {

    return <div className="ComparisonComp">
        <div className="Comparison">
            <div className="ComparisonTable">
                <TableTitles columns={this.state.comparison_columns}/>
                <div className="ComparisonData">
                    <TableData data={this.state.filtered_data}/>
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