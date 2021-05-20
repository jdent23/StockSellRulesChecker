import React, { Component } from 'react';

export class TableData extends Component {



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
                  {data.map(row => <tr id={row[0]} onClick={this.onclick}>{row.map(value => this.props.modifyData(value))}</tr>)}
          </thead>
      </table>
      )
  }
}