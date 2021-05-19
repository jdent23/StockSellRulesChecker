import React, { Component } from 'react';

export class TableTitles extends Component {
    render() {
        var columns = this.props.columns;
        return (
            <table>
                <thead>
                    <tr>
                        <div></div>
                        {columns.map(col => <th>{col.split('_').join(' ')}</th>)}
                    </tr>
                </thead>
            </table>
        );
    }
  }