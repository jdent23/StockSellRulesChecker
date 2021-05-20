import React, { Component } from 'react';

export class TableData extends Component {

  onclick(ev) {
    window.open ("https://www.marketwatch.com/investing/stock/" + ev.target.parentElement.id, "_newtab" );
  }

  render() {
      var data = this.props.data;

      if(data.length < 1) {
        return <div style={{color: "white"}}>No Results</div>
      }



      return (
        <table>
          <thead>
                  {data.map(row => <tr id={row[0]} onClick={this.onclick}>{row.map(value => <th>{value.toString()}</th>)}</tr>)}
          </thead>
      </table>
      )
  }
}