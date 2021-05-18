import React, { Component } from 'react';

export class TableData extends Component {
    render() {
        var data = this.props.data;
        return (
          <table>
            <thead>
                    {data.map(row => <tr>{row.map(value => <th>{value.toString()}</th>)}</tr>)}
            </thead>
        </table>
        )
    }
  }