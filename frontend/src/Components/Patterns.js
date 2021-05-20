import React, { Component } from 'react';
import { TableTitles } from './TableTitles';
import { TableData } from './TableData';
import { SearchOptions } from './SearchOptions';
import { ApplyFilter } from './SearchOptions';

export class Patterns extends Component {
  constructor(props) {
    super(props);
    this.state = {
      patterns_columns: [],
      patterns_data: [[]],
      search_options: {}
    };

    this.setSearchOptions = function(new_search_options) {
      this.setState({search_options: new_search_options})
    }.bind(this);
  }

  componentDidMount() {
    this.setState({ isLoading: true });
 
    fetch("http://localhost:5000/api/chart_patterns")
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(res => this.setState({ patterns_columns: res.patterns_columns, patterns_data: res.patterns_data, filtered_data: res.patterns_data}))
      .catch(error => this.setState({ error }));
  }



  render() {

    return <div className="PatternsComp">
        <div className="Patterns">
            <div className="PatternsTable">
                <TableTitles columns={this.state.patterns_columns} notifyRule={this.props.notifyRule}/>
                <div className="PatternsData">
                    <TableData data={this.state.patterns_data.filter((data_row) => ApplyFilter(this.state.patterns_columns, data_row, this.state.search_options))}/>
                </div>
            </div>
        </div>

        <form action="http://localhost:5000/export_table" method="get">
              <input type="submit" value="Download Table"/>
        </form>
        <SearchOptions option_names={this.state.patterns_columns}
                      data_types={this.state.patterns_data[0].map(value => typeof(value))}
                      set_search_options={this.setSearchOptions}/>
    </div>
  }
}